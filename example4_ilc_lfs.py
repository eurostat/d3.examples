#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 00:19:41 2018

@author: gjacopo
"""

#%%      
from __future__ import print_function

import os, re#analysis:ignore
from functools import reduce

import metadata
import build_chord

#%%      
#==============================================================================
# CHORD SCRIPT
#==============================================================================

# control the indicators you want to select
INDICATOR_CROSS = [[r'^ilc'],[r'^lfs']]
INDICATOR_KEEP  = reduce(lambda x,y: x + y, INDICATOR_CROSS)

DIMENSION_DROP  = ['time','geo']

INDICATORxDIMENSION = '%sx%s' % (metadata.INDICATOR, metadata.DIMENSION)
ODIR            = '../__temp__'

df = metadata.meta2data(ind= {'keep': INDICATOR_KEEP}, 
                        dim= {'drop': DIMENSION_DROP})

# select some of interest
SELIND = []
#x = df[metadata.DIMENSION].isin(['nace_r2', 'nace_r1', 'deg_urb'])
#SELIND = df[x][metadata.INDICATOR].unique()
x, y, z =                                   \
    df[metadata.DIMENSION]=='geo',          \
    df[metadata.LABEL].str.len()>2,         \
    df[metadata.LABEL].str[:3].isin(['EU1','EA1','EU2','EA2','OTH','NON','NMS'])
selind1 = df[x & y & ~z][metadata.INDICATOR].unique()
SELIND = list(set(SELIND).union(set(selind1)))

# filter
#x, y =                                      \
#    df[metadata.DIMENSION]=='geo',          \
#    df[metadata.INDICATOR].isin(SELIND)
#df = df[~x & y]
SELIND = df[metadata.INDICATOR].unique()
df = df[df[metadata.INDICATOR].isin(SELIND)]

[ind0, ind1, df_cross] = build_chord.meta2cross(df, cross=INDICATOR_CROSS)

df_edges = build_chord.adjacency2edges(df_cross, ind0, ind1)

#build_chord.adjacency2json(df_cross, dim=ind0, ind=ind1,
#                           oifn = metadata.INDICATOR, odfn = metadata.DIMENSION, 
#                           oixdfn = INDICATORxDIMENSION, odir=ODIR)

MINCOMMON = 15
reduced_df_edges = df_edges[df_edges['value']>=MINCOMMON]
ilc_ind, lfs_ind =  \
    reduced_df_edges['source'].unique(), reduced_df_edges['target'].unique()


lfs_new_ind = ['lfsa_ergaed', 'lfsa_argaed', 'lfsa_ewpshi', 'lfsa_ehomp', 'lfsq_urgan', 'lfsa_urgacob', 'lfsa_pgacws', 'lfsa_ergacob', 'lfsa_urgan', 'lfsa_ergan', 
 'lfsa_ewpsun', 'lfsa_ewpsat', 'lfsa_ewpeve', 'lfsa_upgacob', 'lfsa_argacob', 'lfsa_upgan', 'lfsa_argan']

reduced_df_edges = reduced_df_edges[reduced_df_edges['target'].isin(lfs_new_ind)]
ilc_ind, lfs_ind =  \
    reduced_df_edges['source'].unique(), reduced_df_edges['target'].unique()
