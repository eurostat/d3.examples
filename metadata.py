#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:20:49 2018

@author: gjacopo
"""

#%%
from __future__ import print_function

import os, re#analysis:ignore
import os.path
import warnings

from collections import OrderedDict
from functools import reduce

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
        self.__table = None
        self.__basename = ''
        
    #/************************************************************************/
    @property
    def table(self):
        return self.__table
                
    #/************************************************************************/
    @property
    def basename(self):
        if self.__basename in ('',None):
            self.__basename = '%s.%s' % (self.BULK_BASE_FILE, self.BULK_BASE_EXT)
            if self.BULK_BASE_ZIP not in ('',None):
                self.__basename = '%s.%s' % (self.__basename, self.BULK_BASE_ZIP)
        return self.__basename
           
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
        self.__table = pd.read_csv(base, header=None, sep=self.SEP, names=self.NAMES)

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
        kwargs.update({'header': None, 
                       'encoding': kwargs.get('encoding') or None,
                       'skip_blank_lines': kwargs.get('skip_blank_lines') or True, 
                       'memory_map': kwargs.get('memory_map') or True,
                       'error_bad_lines': kwargs.get('error_bad_lines') or False, 
                       'warn_bad_lines': kwargs.get('warn_bad_lines') or True, 
                       'names': self.NAMES, 'sep': self.SEP})
        if self.basename.endswith('gz'):
            kwargs.update({'compression': 'gzip'})
        else:
            kwargs.update({'compression': 'infer'})
        # run the pandas.read_table method
        self.__table = pd.read_table(url, **kwargs)

    #/************************************************************************/
    def load(self, base):
        if isinstance(base, np.array):
            if pd is not None:
                base = pd.DataFrame(data=base)
            else:
                pass
        elif not isinstance(base, pd.DataFrame):
            raise IOError('wrong value for METABASE parameter')
        self.__table = base

    #/************************************************************************/
    def filter(self, **kwargs):
        kw_ind, kw_dim = kwargs.pop('ind', {}), kwargs.pop('dim', {})
        if kw_ind == {} and kw_dim == {}:
            warnings.warn('No filter applied')
            return self.__table
        elif not (isinstance(kw_ind, dict) and isinstance(kw_dim, dict)):
            raise IOError('Wrong type for keyword arguments "IND" and/or "DIM"')
        if kw_ind != {}:
            ind_keep, ind_drop = kw_ind.pop('keep', None), kw_ind.pop('drop', None)
        if kw_dim != {}:
            dim_keep, dim_drop = kw_dim.pop('keep', None), kw_dim.pop('drop', None)
        if all([arg in ([],None) for arg in [ind_keep, ind_drop, dim_keep, dim_drop]]):
            warnings.warn('No filter applied')
            return self.__table
        else:
            df = self.__table
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
        # self.__table = df
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
    # #NAMES           = ["title"	"code"	"type"	"last update of data"	"last table structure change"	"data start"	"data end"	"values"]
    SEP             = '\s+'
 
    #/************************************************************************/
    def __init__(self):
        # super(ToC,self).__init__()
        self.__table = None
        self.__basename = ''
               
    #/************************************************************************/
    @property
    def table(self):
        return self.__table 
                
    #/************************************************************************/
    @property
    def basename(self):
        if self.__basename in ('',None):
            self.__basename = '%s_%s.%s' % (self.BULK_BASE_FILE, self.LANG, self.BULK_BASE_EXT)
        return self.__basename
           
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
        self.__table = pd.read_csv(base, header='infer', sep=self.SEP
                                   # names=self.NAMES
                                   )
        
    #/************************************************************************/
    def filter(self, **kwargs):
        pass
    
def toc2table(**kwargs):    
    toc = ToC()
    try:
        toc.read(**kwargs)
        assert toc.table is not None
    except:
        print ("burp")
        toc.download()        
    return toc.filter(**kwargs)
    