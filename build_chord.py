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

import metadata


#%%      
#==============================================================================
# CHORD FUNCTIONS
#==============================================================================

def __filedirexists(file):
    return os.path.exists(os.path.abspath(os.path.dirname(file)))
     
def data2adjacency(df):         
    df_unique = df.drop_duplicates([metadata.INDICATOR, metadata.DIMENSION])
    # df_test = df_unique.pivot(index='indicator', columns='dimension', values='label')
    df_unique.drop(columns=metadata.LABEL)
    df_cross = pd.crosstab(df_unique[metadata.INDICATOR], df_unique[metadata.DIMENSION])
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
        
def meta2cross(df, cross=None):  
    
    print (df.index)
    idx = {0: [], 1: []}
    if not cross in ([],None):
        if not isinstance(cross, (list,tuple)) or len(cross)!=2:     
            cross = [cross,]
        for i in [0,1]:
            if cross[i] in ([],None):   break
            regexp = '|'.join(cross[i])
            _idx = df.loc[df[metadata.INDICATOR].str.contains(regexp, regex=True)].index.tolist()
            idx[i] = idx[i] + _idx
    if not all([_idx in ([],None) for _idx in idx.values()]):
        index = idx[0] + idx[1]
    else:
        idx[0] = idx[1] = df.index
        index = df.index
    ## two rounds of drop_duplicates to keep only non-unique (DIMENSION,LABEL) pairs 
    #df1 = df.drop_duplicates(subset=[metabase.DIMENSION, metabase.LABEL])
    #df2 = df.loc[(df.index).difference(df1.index)]
    #uni_index = df2.drop_duplicates(subset=[metabase.DIMENSION, metabase.LABEL]).index
    ## note also: 
    #df_group = df.groupby(by=[metabase.DIMENSION, metabase.LABEL])
    #df_dimlab = df_group.count()
    ## keep only non-unique (DIMENSION,LABEL) pairs 
    #df_dimlab = df_dimlab[df_dimlab[metabase.INDICATOR] > 1]

    df_cross = pd.pivot_table(df, index=[metadata.DIMENSION, metadata.LABEL], columns=[metadata.INDICATOR], aggfunc=len, fill_value=0)
    df_cross = df_cross.T.dot(df_cross)
    # # alternative solution
    # df['value'] = 1
    # df1 = pd.pivot_table(df, index=[metabase.DIMENSION, metabase.LABEL], values='value', columns=metabase.INDICATOR, fill_value=0)
    np.fill_diagonal(df_cross.values, 0)
    
    #s = df_cross.sum(axis=0) 
    #index = s[s != 0].index.tolist()
    df_cross.reindex(index = index, columns = index, fill_value=0)

    return [df.ix[pd.Index(idx[0]),metadata.INDICATOR].unique().tolist(), 
            df.ix[pd.Index(idx[1]),metadata.INDICATOR].unique().tolist(), 
            df_cross]

def adjacency2json(df_adjacency, **kwargs):
    dimensions, indicators = kwargs.pop('dim',[]), kwargs.pop('ind',[]) 
    odir, ofmt = kwargs.pop('odir','.'), kwargs.pop('ofmt','json') 
    oifn, odfn = kwargs.pop('oifn', metadata.INDICATOR), kwargs.pop('odfn', metadata.DIMENSION)
    oixdfn = kwargs.pop('oixdfn','%sx%s' % (metadata.INDICATOR, metadata.DIMENSION))

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

