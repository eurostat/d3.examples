#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 23:56:25 2018

@author: gjacopo
"""

import os
import warnings

try:
    import json
except:
    try:
        import simplejson as json#analysis:ignore
    except:
        warnings.warn("Package simplejson/json not imported")

#%%      
#==============================================================================
# ToC FUNCTION
#==============================================================================

def __filedirexists(file):
    return os.path.exists(os.path.abspath(os.path.dirname(file)))

def toc2json(toc, **kwargs):
    odir, ofmt = kwargs.pop('odir','.'), kwargs.pop('ofmt','json') 
    otocfn = kwargs.pop('otocfn','ToC')

    ofn = '%s/%s.%s' % (odir, otocfn, ofmt)
    if __filedirexists(ofn):
        with open(ofn, 'w') as f:
            # json.dump(toc, f, indent=4) # sort_keys=True
            f.write('var treeData = %s;' % json.dumps(toc, indent=4))
    

 