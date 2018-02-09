#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:20:49 2018

@author: gjacopo
"""

#%%      
#==============================================================================
# CHORD SCRIPT
#==============================================================================

from __future__ import print_function

import os, re#analysis:ignore

from .. import metabase#analysis:ignore
from . import adjacency_chord


INDICATOR_KEEP  = ['icw'] # ['ilc_peps', 'ilc_pees']

DIMENSION_DROP  = ['geo', 'time']

INDICATORxDIMENSION = '%sx%s' % (metabase.INDICATOR, metabase.DIMENSION)
ODIR            = '.'

[dimensions, indicators, df_adjacency] = \
    adjacency_chord.meta2adjacency(ind_keep = INDICATOR_KEEP, dim_drop = DIMENSION_DROP)
adjacency_chord.adjacency2json(df_adjacency, dim=dimensions, ind=indicators,
               oifn = metabase.DIMENSION, odfn = metabase.DIMENSION, 
               oixdfn = INDICATORxDIMENSION, odir=ODIR)

