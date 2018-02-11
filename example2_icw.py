#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:20:49 2018

@author: gjacopo
"""

#%%      
from __future__ import print_function

import os, re#analysis:ignore

import metabase
import build_chord

#%%      
#==============================================================================
# CHORD SCRIPT
#==============================================================================

# control the indicators you want to select
INDICATOR_KEEP  = ['icw']

DIMENSION_DROP  = ['geo', 'time']

INDICATORxDIMENSION = '%sx%s' % (metabase.INDICATOR, metabase.DIMENSION)
ODIR            = 'example2'

df = build_chord.meta2data(ind= {'keep': INDICATOR_KEEP}, 
                           dim= {'drop': DIMENSION_DROP})

[dimensions, indicators, df_adjacency] = build_chord.data2adjacency(df)

build_chord.adjacency2json(df_adjacency, dim=dimensions, ind=indicators,
                           oifn = metabase.INDICATOR, odfn = metabase.DIMENSION, 
                           oixdfn = INDICATORxDIMENSION, odir=ODIR)

