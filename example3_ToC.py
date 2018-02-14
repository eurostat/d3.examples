#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 23:11:48 2018

@author: gjacopo
"""


#%%      
from __future__ import print_function

import os, re#analysis:ignore

import metadata
import create_tree

#%%      
#==============================================================================
# CHORD SCRIPT
#==============================================================================

# control the indicators you want to select
OFILE           = 'ToC'
ODIR            = './example3'

table = metadata.toc2table()
create_tree.toc2json(table, odir=ODIR, otocfn = OFILE, ofmt='json')
