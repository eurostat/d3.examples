#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:20:49 2018

@author: gjacopo
"""

#%%
from __future__ import print_function

import os, re#analysis:ignore
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

class Data(object):
    BULK_DOMAIN     = 'ec.europa.eu/eurostat/estat-navtree-portlet-prod'
    BULK_QUERY      = 'BulkDownloadListing'
    BULK_BASE_FILE  = 'metabase.txt' 
    BULK_BASE_ZIP   = 'gz' 
    LANG            = 'en'
    SORT            = 1
    NAMES           = [INDICATOR, DIMENSION, LABEL]
    SEP             = '\s+'
    
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
        self.__basename = '%s.%s' % (self.BULK_BASE_FILE, self.BULK_BASE_ZIP)
        return self.__basename
           
    #/************************************************************************/
    def read(self, **kwargs):
        path, base = kwargs.get('base'), kwargs.get('base', self.basename)
        if path is not None:
            base = '%s/%s' % (path, base)
        self.__table = pd.read_csv(base, header=None, sep=self.SEP, names=self.NAMES)

    #/************************************************************************/
    def download(self, **kwargs):
        url = '%s/%s' % (self.BULK_DOMAIN, self.BULK_QUERY)
        # retrieve parameters/build url
        if not url.startswith('http'):  url = "http://%s" % url
        if 'path' in kwargs:            url = "%s/%s" % (url, kwargs.pop('path'))
        if 'query' in kwargs:           url = "%s/%s" % (url, kwargs.pop('query'))
        kw = OrderedDict([('sort',self.SORT), ('file', self.basefile)])
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
        indicator_keep, dimension_drop = kwargs.pop('ind_keep', None), kwargs.pop('dim_drop', None)
        if indicator_keep in ([],None) and dimension_drop in ([],None):
            return self.__table
        else:
            df = self.__table
        if  not indicator_keep in ([],None):
            # limit the dataset to SILC data only
            regexp = '|'.join(indicator_keep)
            self.__table = df.loc[df[INDICATOR].str.contains(regexp, regex=True)]
            #search_text = lambda text: bool(re.search('%s' % SILC_KEYWORD, text))
            #df = df.loc[df['indicator'].map(search_text) == True]
        
        if not dimension_drop in ([],None):
            drop_index = reduce(lambda idx1, idx2: idx1.union(idx2),            \
                                [df[df[DIMENSION] == dim].index for dim in dimension_drop])
            df = df.loc[(df.index).difference(drop_index)]
        # self.__table = df
        return df