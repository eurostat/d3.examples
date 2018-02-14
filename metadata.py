#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:20:49 2018

@author: gjacopo
"""

#%%
from __future__ import print_function

import os, re#analysis:ignore
import time
import os.path
import warnings

from collections import OrderedDict
from functools import reduce
from itertools import takewhile
import copy

try:
    import numpy as np#analysis:ignore
except:
    raise IOError("Package numpy not imported - Requested")
    
try:
    import pandas as pd
    PDVERS = int(pd.__version__.split('.')[1])
except:
    PDVERS = 0 # unknown
    raise IOError("Package pandas not imported - Requested")

try:
    import json
except:
    try:
        import simplejson as json#analysis:ignore
    except:
        warnings.warn("Package simplejson/json not imported")
  
try:                                
    import requests # urllib2
except ImportError:                 
    raise IOError


#%%
#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

INDICATOR       = 'INDICATOR'
DIMENSION       = 'DIMENSION'
LABEL           = 'LABEL'


#%%
#==============================================================================
# METHOD DEFINITION
#==============================================================================

class Metabase(object):
    BULK_DOMAIN     = 'ec.europa.eu/eurostat/estat-navtree-portlet-prod'
    BULK_QUERY      = 'BulkDownloadListing'
    BULK_BASE_FILE  = 'metabase' 
    BULK_BASE_EXT   = 'txt' 
    BULK_BASE_ZIP   = 'gz' 
    LANG            = 'en'
    SORT            = 1
    NAMES           = [INDICATOR, DIMENSION, LABEL]
    SEP             = '\s+'
    
    #/************************************************************************/
    @staticmethod
    def _fileexists(file):
        return os.path.exists(os.path.abspath(file))

    #/************************************************************************/
    def __init__(self):
        self._table = None
        self._basename = ''
        
    #/************************************************************************/
    @property
    def table(self):
        return self._table
    @table.setter
    def table(self, table):
        self._table = table
               
    #/************************************************************************/
    @property
    def basename(self):
        if self._basename in ('',None):
            self._basename = '%s.%s' % (self.BULK_BASE_FILE, self.BULK_BASE_EXT)
            if self.BULK_BASE_ZIP not in ('',None):
                self._basename = '%s.%s' % (self._basename, self.BULK_BASE_ZIP)
        return self._basename
           
    #/************************************************************************/
    def read(self, **kwargs):
        path, base = kwargs.get('path'), kwargs.get('base', self.basename)
        if base in ('',None):
            base = self.basename
        if path is not None:
            base = '%s/%s' % (path, base)
        if not self._fileexists(base):
            warnings.warn('Base file %s not found' % base)
            return
        self.table = pd.read_csv(base, header=None, sep=self.SEP, names=self.NAMES)

    #/************************************************************************/
    def download(self, **kwargs):
        url = '%s/%s' % (self.BULK_DOMAIN, self.BULK_QUERY)
        # retrieve parameters/build url
        if not url.startswith('http'):  url = "http://%s" % url
        if 'path' in kwargs:            url = "%s/%s" % (url, kwargs.pop('path'))
        if 'query' in kwargs:           url = "%s/%s" % (url, kwargs.pop('query'))
        kw = OrderedDict([('sort',self.SORT), ('file', self.basename)])
        _izip_replicate = lambda d : [[(k,i) for i in d[k]] if isinstance(d[k], (tuple,list))   \
            else (k, d[k])  for k in d]          
        filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kw)])
        url = "%s?%s" % (url, filters)
        try:
            session = requests.session()
        except:
            raise IOError('wrong definition for SESSION parameter')
        else:
            response = session.head(url)
        try:
            response.raise_for_status()
        except:
            raise IOError('wrong request formulated')  
        else:
            # status = response.status_code
            response.close()
        # set some default values (some are already default values for read_table)
        kwargs.update({'header': kwargs.get('header') or None, 
                       'encoding': kwargs.get('encoding') or None,
                       'skip_blank_lines': kwargs.get('skip_blank_lines') or True, 
                       'memory_map': kwargs.get('memory_map') or True,
                       'error_bad_lines': kwargs.get('error_bad_lines') or False, 
                       'warn_bad_lines': kwargs.get('warn_bad_lines') or True})
        if self.NAMES not in (None,[]):
            kwargs.update({'names': self.NAMES})
        if self.SEP not in (None,[]):
            kwargs.update({'sep': self.SEP})
        if self.basename.endswith('gz'):
            kwargs.update({'compression': 'gzip'})
        else:
            kwargs.update({'compression': 'infer'})
        # run the pandas.read_table method
        self.table = pd.read_table(url, **kwargs)

    #/************************************************************************/
    def load(self, base):
        if isinstance(base, np.array):
            if pd is not None:
                base = pd.DataFrame(data=base)
            else:
                pass
        elif not isinstance(base, pd.DataFrame):
            raise IOError('wrong value for METABASE parameter')
        self.table = base

    #/************************************************************************/
    def filter(self, **kwargs):
        kw_ind, kw_dim = kwargs.pop('ind', {}), kwargs.pop('dim', {})
        if kw_ind == {} and kw_dim == {}:
            warnings.warn('No filter applied')
            return self.table
        elif not (isinstance(kw_ind, dict) and isinstance(kw_dim, dict)):
            raise IOError('Wrong type for keyword arguments "IND" and/or "DIM"')
        if kw_ind != {}:
            ind_keep, ind_drop = kw_ind.pop('keep', None), kw_ind.pop('drop', None)
        if kw_dim != {}:
            dim_keep, dim_drop = kw_dim.pop('keep', None), kw_dim.pop('drop', None)
        if all([arg in ([],None) for arg in [ind_keep, ind_drop, dim_keep, dim_drop]]):
            warnings.warn('No filter applied')
            return self.table
        else:
            df = self.table
        if  not ind_keep in ([],None):
            if not isinstance(ind_keep, (list,tuple)):  ind_keep = [ind_keep,]
            regexp = '|'.join(ind_keep)
            df = df.loc[df[INDICATOR].str.contains(regexp, regex=True)]
            #search_text = lambda text: bool(re.search('%s' % regexp, text))
            #df = df.loc[df['indicator'].map(search_text) == True]
        if df.empty:                    return df
        if  not ind_drop in ([],None):
            if not isinstance(ind_drop, (list,tuple)):  ind_drop = [ind_drop,]
            regexp = '|'.join(ind_drop)
            df = df.loc[~df[INDICATOR].str.contains(regexp, regex=True)]
        if df.empty:                    return df
        if not dim_drop in ([],None):
            if not isinstance(dim_drop, (list,tuple)):  dim_drop = [dim_drop,]
            drop_index = reduce(lambda idx1, idx2: idx1.union(idx2),            \
                                [df[df[DIMENSION] == dim].index for dim in dim_drop])
            df = df.loc[(df.index).difference(drop_index)]
        if df.empty:                    return df
        if not dim_keep in ([],None):
            if not isinstance(dim_keep, (list,tuple)):  dim_keep = [dim_keep,]
            keep_index = reduce(lambda idx1, idx2: idx1.union(idx2),            \
                                [df[df[DIMENSION] == dim].index for dim in dim_keep])
            df = df.loc[keep_index]
        # self._table = df
        return df

def meta2data(**kwargs):    
    metabase = Metabase()
    try:
        metabase.read(**kwargs)
    except:
        metabase.download()        
    return metabase.filter(**kwargs)

class ToC(Metabase): # we are just lazy...
    #BULK_DOMAIN     = 'ec.europa.eu/eurostat/estat-navtree-portlet-prod'
    #BULK_QUERY      = 'BulkDownloadListing'
    BULK_BASE_FILE  = 'table_of_contents' 
    #BULK_BASE_EXT   = 'txt' 
    LANG            = 'en'
    #SORT            = 1
    NAMES           = None
    # #NAMES           = ["title"	"code"	"type"	"last update of data"	"last table structure change"	"data start"	"data end"	"values"]
    SEP             = '\s+'
    INDENTLEVEL     = 4
                
    #/************************************************************************/
    @property
    def basename(self):
        if self._basename in ('',None):
            self._basename = '%s_%s.%s' % (self.BULK_BASE_FILE, self.LANG, self.BULK_BASE_EXT)
        return self._basename
           
    #/************************************************************************/
    def read(self, **kwargs):
        path, base = kwargs.get('path'), kwargs.get('base', self.basename)
        if base in ('',None):
            base = self.basename
        if path is not None:
            base = '%s/%s' % (path, base)
        if not self._fileexists(base):
            warnings.warn('Base file %s not found' % base)
            return
        self.table = pd.read_csv(base, header='infer', sep=self.SEP
                                   # names=self.NAMES
                                   )
        
    #/************************************************************************/
    def filter(self, **kwargs):
        df = self.table
        level = self.INDENTLEVEL
        df['depth'] = df['title'].apply(lambda title: int(sum(1 for _ in takewhile(str.isspace,title)) / level))
        return df
    
    #/************************************************************************/
    def format(self, *arg):
        if arg in ((),None):    table = self.table
        else:                   table = arg[0]
        def obsitem(node, obs):
            depth = obs['depth']
            if depth==0: # and obs['type'] == 'folder' and obs['code']=='data'
                new = OrderedDict([("name", '%s' % obs['title'].lstrip()), ("children", [])])
                node[0].update(new)
                node.append(new["children"])
            elif obs['type'] == 'folder':
                new = OrderedDict([("name", '%s - %s' % (obs['title'].lstrip(),obs['code'])), 
                                   ("children", [])])
                node[depth].append(new)
                if len(node) > depth+1:
                    node[0] = copy.deepcopy(node[0]) # deepcopy!!!
                    node[depth+1] = new['children']
                else:
                    node.append(new['children'])      
            elif obs['type'] == 'dataset':
                new = OrderedDict([("name", '%s (%s)' % (obs['code'],obs['title'].lstrip())), 
                                   ("size", 1)])
                node[depth].append(new)
        tree = OrderedDict()
        node = [tree,]
        [obsitem(node, obs) for _, obs in table.iterrows()]
        return tree

def toc2table(**kwargs):    
    toc = ToC()
    try:
        print('Trying to read the input table of contents from cache...')
        toc.read(**kwargs)
        assert toc.table is not None
    except:
        # time.sleep(0.5)
        print('Downloading the bulk table from bulk facility...')
        toc.download(header='infer')  
    return toc.format(toc.filter())
    