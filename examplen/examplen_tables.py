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

from . import metabase


#%%      
#==============================================================================
# CHORD FUNCTIONS
#==============================================================================
 
def meta2formats(**kwargs):
    metadata = metabase.data()
    metadata.download()        
    df = metadata.filter(**kwargs)
    
    # list all present SILC INDICATORs 
    indicators = df.groupby([metabase.INDICATOR]).groups.keys()
    # list all DIMENSIONs used by SILC datasets 
    dimensions = df.groupby([metabase.DIMENSION]).groups.keys()
    
    # group together all labels used for a given [INDICATOR, DIMENSION] pair
    df_group = df.groupby(by=[metabase.INDICATOR, metabase.DIMENSION])
    formats = df_group[metabase.LABEL].apply(list).apply(sorted)
    #format_sets = df_group.aggregate(lambda x: set(x))
    #format_series = df_group.apply(lambda tdf: pd.Series(dict([[vv,tdf[vv].unique().tolist()] for vv in tdf if vv not in ['indicator','dimension']])))
    
    #if not DIMENSION_DROP in (None, []):
    #    label_lists.drop('geo', level=1, axis=0, inplace=True)
    #    label_lists.drop('time', level=1, axis=0, inplace=True)
    
    dimension_lists = df.groupby(metabase.DIMENSION)[metabase.INDICATOR].apply(list)#analysis:ignore
    
    # define the dictionary of unique "formats" (that is a list of labels used together
    # of a same indicator) indexed by the list of DIMENSIONs
    unique_formats = dict.fromkeys(dimensions)
    # "uniquify" the list of list stored in FORMAT_LISTS.xs(DIM, level='dimension').values
    # for each DIM in the list DIMENSION
    [unique_formats.update({dim: list(map(list, set(map(lambda i: tuple(i), formats.xs(dim, level=metabase.DIMENSION).values))))}) 
        for dim in dimensions]
    # create an ordered dict UNIQUE_FORMATS of unique format lists based on the lenght of the label list
    [unique_formats.update({dim: OrderedDict(zip(range(1,len(unique_formats[dim])+1),sorted(unique_formats[dim], key= lambda x: len(x))))}) \
                          for dim in dimensions]

    # note that:
    # all([list(unique_formats['age'].values())[i] == unique_formats['age'][i+1] for i in range(len(unique_formats['age']))]) is True

    return dimensions, indicators, formats, unique_formats

def dimlab2json(unique_formats, formats, **kwargs):
    dimensions, indicators = kwargs.pop('dim',[]), kwargs.pop('ind',[]) 
    odir, ofmt = kwargs.pop('odir','.'), kwargs.pop('ofmt','csv') 
    oixdfn = kwargs.pop('oixdfn','%sx%s' % (metabase.INDICATOR, metabase.DIMENSION))
    odxffn = kwargs.pop('odxffn','%sFORMATS' % metabase.DIMENSION)
    ofxifn = kwargs.pop('ofxifn','FORMATSx%s' % metabase.INDICATOR)
    olxffn = kwargs.pop('olxffn','%sVALUExFORMAT' % metabase.LABEL)
    labcols = kwargs.pop('labcols', ['%s' % metabase.LABEL,])
    
    with open('%s/%s.%s' % (odir, odxffn, 'json'), 'w') as f:
        json.dump(unique_formats, f, indent=4, sort_keys=True)
 
    # solution 2 - incomplete
    #inddimlab['dimlabel'] = inddimlab[['dimension', 'labelcat']].astype(str).apply(lambda x: '_'.join(x), axis=1)
    #labxind = inddimlab.pivot(index='dimlabel', columns='indicator', values='labelcat').clip_upper(1)
    #labxind.fillna(0,inplace=True)
    #labxind = inddimlab.astype(int)
    
    # solution 3: incomplete, slow and complex...
    #inddimlab['dimlabel'] = inddimlab[['dimension', 'labelcat']].astype(str).apply(lambda x: '_'.join(x), axis=1)
    #labxind = pd.concat([inddimlab['indicator'],
    #           pd.get_dummies(inddimlab['dimlabel'].astype('category'), dummy_na=0)], axis=1)
    #labxind = labxind.groupby(by='indicator').sum(axis=1)
    #labxind = labxind.transpose()
    #labxind['dimension'], labxind['labelcat'] = [pd.Series(labxind.index).astype(str).apply(lambda x: x.split('_')[i]).get_values() for i in (0,1)]
    #labxind = labxind[['dimension','labelcat'] + [col for col in labxind.columns.tolist() if col not in ('dimension','labelcat')]]
    #labxind.reset_index(drop=True,inplace=True)
  
    # create a dictionary of concatenated labels; this shall preserve the order
    # of formats... we also invert the {key: value} pair
    unique_formats_cat = dict.fromkeys(unique_formats)
    [unique_formats_cat.update({dim: OrderedDict(zip(['_'.join(value) for value in unique_formats[dim].values()], unique_formats[dim].keys()))}) \
                          for dim in dimensions]
    # or equivalently:
    #import copy
    #unique_formats_cat = copy.deepcopy(unique_labels)
    #[unique_formats_cat[dim].update({'_'.join(unique_formats_cat[dim][key]): key for key in unique_formats_cat[dim].keys()}) \
    #                                 for dim in dimensions]
    unique_formats_cat = reduce(lambda x,y: {**x, **y}, [unique_formats_cat[dim] for dim in dimensions])
    # note that in Python<3.5 we shall write:
    # unique_formats_cat = reduce(lambda x,y: x.update(y), [unique_formats_cat[dim] for dim in dimensions])

    # create a new table from the "formats" FORMAT_LISTS by adding to it a column that
    # stores the strings of concatenated labels
    format_lists_cat = pd.concat([formats, formats.map(lambda x: '_'.join(x)).rename('labelcat', inplace=True)], axis=1)

    format_lists_cat['labelcat'] = format_lists_cat['labelcat'].map(unique_formats_cat)
    format_lists_cat.drop(columns=metabase.LABEL, inplace=True)
    
    inddimlab = format_lists_cat.reset_index().sort_values(by=[metabase.DIMENSION,'labelcat'])
    # solution 1
    inddimlab['labelcat2'] = inddimlab['labelcat']
    #labxind = pd.pivot_table(inddimlab, index=['dimension','labelcat'], values='labelcat2', columns='indicator', fill_value=0)
    #labxind = labxind.astype(int).clip_upper(1)
    # note that we deal with NaN and float values when writing to csv
    fmtxind = pd.pivot_table(inddimlab, index=[metabase.DIMENSION,'labelcat'], values='labelcat2', columns=metabase.INDICATOR)
    fmtxind = fmtxind.clip_upper(1)
    fmtxind.reset_index(inplace=True)
    fmtxind['format'] = fmtxind[[metabase.DIMENSION,'labelcat']].astype(str).apply(lambda x: '_fmt{}_{}_'.format(x[1],x[0]), axis=1)
    fmtxind = fmtxind[['format'] + list(indicators)]
    
    with open('%s/%s.%s' % (odir, ofxifn, ofmt), 'w') as f:
        fmtxind.to_csv(f, index=False, header=True, sep=',', float_format='%d', na_rep='')
    
    # build the table providing for every indicator and every dimension 
    # the format used if it is actually the case
    indxdim = format_lists_cat.unstack(metabase.DIMENSION) #, fill_value=NaN)
    indxdim.columns = indxdim.columns.droplevel()
    
    with open('%s/%s.%s' % (odir, oixdfn, ofmt), 'w') as f:
        indxdim.to_csv(f, index=True, header=True, sep=',', float_format='%d', na_rep='')

    # for dim in dimensions:
    dim = 'age'    
    labels = list(set(reduce(lambda x,y: x+y ,list(unique_formats[dim].values()))))
    labels.sort()
    formats = ['_fmt%s_%s_' % (k,dim) for k in unique_formats[dim].keys()]
    labvalxform=pd.DataFrame(columns=labcols + formats)
    for i in range(len(labels)):
        labvalxform.loc[i] = len(labcols) * [np.NaN] + [1 if labels[i] in list(unique_formats[dim].values())[j] else np.NaN for j in range(len(formats))]
    labvalxform[metabase.LABEL] = pd.Series(labels)
    labvalxform['variable'] = dim
    
    with open('%s/%s_%s.%s' % (odir, olxffn, dim, ofmt), 'w') as f:
        labvalxform.to_csv(f, index=False, header=True, sep=',', float_format='%d', na_rep='')

#%%      
#==============================================================================
# METADATA ANALYSIS
#==============================================================================

INDICATOR_KEEP  = ['icw'] # ['ilc_peps', 'ilc_pees']

DIMENSION_DROP  = ['geo', 'time']

LABELVALUExFORMATcols = ['label','variable', 'start', 'end', 'sexcl', 'eexcl', 'type']

INDICATORxDIMENSION = '%sx%s' % (metabase.INDICATOR, metabase.DIMENSION)

FORMATxINDICATOR = 'FORMATxINDICATOR'
LABELVALUExFORMAT = 'LABELVALUExFORMAT'

DIMENSIONFORMATS = 'DIMENSIONFORMATS'

#OFMT            = 'csv'
#ODIR            = '.'

dimensions, indicators, formats, unique_formats =   \
    meta2formats(ind_keep = INDICATOR_KEEP, dim_drop = DIMENSION_DROP)
dimlab2json(unique_formats, formats, labcols = LABELVALUExFORMATcols,
            odxffn = DIMENSIONFORMATS, ofxifn = FORMATxINDICATOR,
            oixdfn = INDICATORxDIMENSION, olxffn = LABELVALUExFORMAT)



