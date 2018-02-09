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

import metabase


#%%      
#==============================================================================
# CHORD FUNCTIONS
#==============================================================================

def __filedirexists(file):
    return os.path.exists(os.path.exists(os.path.dirname(file)))

def meta2adjacency(**kwargs):    
    metadata = metabase.Data()
    metadata.download()        
    df = metadata.filter(**kwargs)
     
    df_unique = df.drop_duplicates([metabase.INDICATOR, metabase.DIMENSION])
    # df_test = df_unique.pivot(index='indicator', columns='dimension', values='label')
    df_unique.drop(columns=metabase.LABEL)
    df_cross = pd.crosstab(df_unique[metabase.INDICATOR], df_unique[metabase.DIMENSION])
    df_cross['dumb'] = 0
    df_cross = df_cross.T
    df_cross['dumber'] = 0
    df_cross.loc['dumb','dumber'] = -1
    df_crossT = df_cross
    df_cross = df_crossT.T
    # note that at this stage, indicators and dimensions are reordered
    #a dimensions, indicators = df_cross.index.tolist(), df_cross.columns.tolist()
    indicators, dimensions = df_cross.index.tolist(), df_cross.columns.tolist()
    # df_crossT = df_cross.T
    
    #idx = indicators + dimensions 
    idx = dimensions + indicators
    df_cross = df_cross.reindex(index = idx, columns = idx, fill_value=0)
    df_crossT = df_crossT.reindex(index = idx, columns = idx, fill_value=0)
    
    return [dimensions, indicators, pd.DataFrame(df_cross.values | df_crossT.values, index = idx, columns = idx)]
    # note: df_cross | df_crossT generates a NotImplementedError error type        
        
def adjacency2json(df_adjacency, **kwargs):
    dimensions, indicators = kwargs.pop('dim',[]), kwargs.pop('ind',[]) 
    odir, ofmt = kwargs.pop('odir','.'), kwargs.pop('ofmt','json') 
    oifn, odfn = kwargs.pop('oifn', metabase.INDICATOR), kwargs.pop('odfn', metabase.DIMENSION)
    oixdfn = kwargs.pop('oixdfn','%sx%s' % (metabase.INDICATOR, metabase.DIMENSION))

    ofn = '%s/%s.%s' % (odir, oixdfn, ofmt)
    if __filedirexists(ofn):
        with open(ofn, 'w') as f:
            #s = str(df_adjacency.values.tolist())    
            #f.write('var matrix = %s;' % s.replace('-1','emptyStroke'))
            f.write('var matrix = %s;' % df_adjacency.values.tolist())
    #df_adjacency.to_json('%s/%s.%s' % (odir, oixdfn, ofmt), orient='split')
    #with open('%s/%s.%s' % (odir, oixdfn, ofmt), 'w') as f:
    #    json.dump(df_adjacency.values.tolist())
    
    ofn = '%s/%s.%s' % (odir, odfn, ofmt)
    if __filedirexists(ofn) and dimensions is not None:
        with open(ofn, 'w') as f:
            # json.dump('var %s = %s;' % (DIMENSION,dimensions), f)
            s = str(dimensions)    
            #a: f.write('var Dimension = %s;' % s.replace('dumber',''))
            f.write('var Dimension = %s;' % s.replace('dumb',''))
            
    ofn = '%s/%s.%s' % (odir, oifn, ofmt)
    if __filedirexists(ofn) and indicators is not None:
        with open(ofn, 'w') as f:
            # json.dump({INDICATOR:indicators}, f)
            s = str(indicators)    
            # a: f.write('var Indicator = %s;' % s.replace('dumb',''))
            f.write('var Indicator = %s;' % s.replace('dumber',''))

