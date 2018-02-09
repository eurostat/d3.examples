#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 10:55:50 2017

@author: gjacopo
"""

# see this page for breakdowns:
# http://ec.europa.eu/eurostat/statistics-explained/index.php/EU_statistics_on_income_and_living_conditions_(EU-SILC)_methodology_-_definition_of_dimensions

from __future__ import print_function

import warnings

try:
    import numpy as np
except:
    raise IOError("Package numpy not imported - Requested")
    
try:
    import pandas as pd
except:
    raise IOError("Package pandas not imported - Requested")

try:
    import json
except:
    try:
        import simplejson as json
    except:
        warnings.warn("Package simplejson/json not imported")

from .. import data
from . import display_force
#from data import EstatDataFrame
#from data import GEO_LABELS, SEX_LABELS, UNIT_LABELS, AGE_LABELS
#from display_force import PackedCircles, ChartWindow
        
#from matplotlib import pyplot as plt
 
DECIMALS    = 5        
           
## define the data
# see this page for breakdowns:
# http://ec.europa.eu/eurostat/statistics-explained/index.php/EU_statistics_on_income_and_living_conditions_(EU-SILC)_methodology_-_definition_of_dimensions

TIME        = ['2008', '2015']

GEO         = ['EU28',                                                      \
               'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES',  \
               'FI', 'FR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',  \
               'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']
# GEO         = "EU28"
                
AGE         = ['TOTAL', 'Y_LT16', 'Y16-24', 'Y25-49', 'Y50-64', 'Y65-74',   \
               'Y_GE75']

SEX         = ['F', 'M', 'T']

UNIT        = ['THS_PER', 'PC_POP']

###############################################################################              
## load the data

INDICATOR       = (u'ilc_peps01', "People at risk of poverty or social exclusion by age and sex")
## http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=tour_occ_nim&lang=en
FILTERS     = {'geo': GEO,
               'sex': SEX,
               'age': AGE,
               }             

idf = data.EstatDataFrame(indicator=INDICATOR)

FILTERS.update({'time': TIME, 'unit': ['THS_PER']})       
df = idf(**FILTERS)
df.drop(['unit'], axis='columns', inplace=True) 

FILTERS.update({'time': TIME, 'unit': ['PC_POP']})       
df_pc = idf(**FILTERS)
df_pc.drop(['unit'], axis='columns', inplace=True) 

###############################################################################              
## do some cleansing/calculation on the input data

# compute change rate (evolution of %ages)
# NO: df['change'] = (df[TIME[1]] - df[TIME[0]]) / df[TIME[0]]
# NO: df_pc['change'] = (df_pc[TIME[1]] - df_pc[TIME[0]]) / df_pc[TIME[0]]
df_pc['change'] = df_pc[TIME[1]] - df_pc[TIME[0]] # change = percentage point
# clean
df_pc.rename(columns={TIME[1]: 'pc_pop'}, inplace=True)
df_pc.drop([TIME[0]], axis='columns', inplace=True) 

# merge tables
df = pd.merge(df, df_pc, how='inner', on=['sex', 'age', 'geo'])

# round data
for i in [0,1]:
    df[TIME[i]] = df[TIME[i]].map(lambda x: round(x,DECIMALS), na_action='ignore')
df['change'] = df['change'].map(lambda x: round(x,DECIMALS), na_action='ignore')

# sort the values in df: this makes the life much easier afterwards
#df.sort_values('pc_pop', ascending=False, inplace=True, na_position='last')
df.sort_values([TIME[0],'change'], ascending=False, inplace=True, na_position='first')
# ascending=False: because we use reverse=True in circle packing algorithm
df.index = range(len(df))

df['age'] = df['age'].map(data.AGE_LABELS)
df['short_geo'] = df['geo']
df['geo'] = df['geo'].map(data.GEO_LABELS)
# df['sex'] = df['sex'].map(data.SEX_LABELS)
  
# special case we get rid of already...
df.replace(to_replace='Germany (until 1990 former territory of the FRG)', value='Germany', inplace=True)

###############################################################################              
## define the "category" variables

category_list = json.dumps(list(np.unique(df['geo'].values)))
# category_list = list([data.GEO_LABELS[geo] for geo in GEO if geo!='EU28'])    

category_df = df[(df['sex']=='T')                       \
              & ~(df['geo']==data.GEO_LABELS['EU28'])   \
              & (df['age']==data.AGE_LABELS['TOTAL'])]
category_df.drop([TIME[0],'pc_pop','sex','age','change'], axis='columns', inplace=True) 
category_df.rename(columns={TIME[1]: 'total', 'geo': 'label', 'short_geo':'short_label'}, inplace=True)
category_df['num_children']=2 # only M/F are displayed

category_data = json.dumps(category_df.to_dict(orient="records"))
category_data.replace('NaN','Infinity') # in case...

###############################################################################              
## prepare data for overall status display and display by sex 

df_status = df[~(df['sex']=='T')                         \
              & ~(df['geo']==data.GEO_LABELS['EU28'])   \
              & (df['age']==data.AGE_LABELS['TOTAL'])]
df_status['id'] = len(df_status) - np.array(df_status['pc_pop']).argsort().argsort() - 1 
# note: this can be retrieved using rank:
#    df_status['change'].rank(ascending=False,method='first')
# while:
#    len(df_status) - df_status['change'].argsort().argsort() - 1
# provides "weird" output
data_status = df_status.to_dict(orient="records")

# prepare the charter considering the display window (with default configuration)
win_status = display_force.ChartWindow(rrange=[1,90], domain=[0,10000]) 

# (x,y) "total" positions for total overlay
rates_status = [np.int(win_status.rScale(d[TIME[1]]))                 \
               if ~np.isnan(d[TIME[1]]) else 1. for d in data_status] 
# note: 2015 rates are sorted already in descending order already
t = display_force.PackedCircles(rad=rates_status)
t.position()
t.plot()
circles = [t.circles[i][:2]                             \
           for i in sorted(range(len(t.circles)), key=lambda k: t.circles[k][2], reverse=True)]
centre = sorted([(int(circ[0]),int(circ[1])) for circ in circles], key=lambda item: item[1],reverse=True)   
# note that we further modify the x-axis depending on the 'sex' of the displayed data
[d.update({'positions': {'total':{'x':win_status.centerX-centre[d['id']][0] + (200 if d['sex']=='F' else -200),   \
                                  'y':win_status.centerY-centre[d['id']][1]    \
                                  }                                             \
                        }                                                       \
          }) for d in data_status]                           

###############################################################################              
## prepare the charter for display by geo area

win_geo = display_force.ChartWindow(rowPos=[275+i*175 for i in range(7)],
                              width=970, height=1300, 
                              rrange=[1,90], domain=[0,10000]) 

posLookup = win_geo.table_cells([geo for geo in GEO if geo!='EU28'])
for geo in GEO:
    if geo=='EU28': continue
    array = [d for d in data_status if d['short_geo']==geo]
    rates = [np.int(win_geo.rScale(d[TIME[1]])) if ~np.isnan(d[TIME[1]]) else 1.  \
            for d in array]
    #c = display_force.PackedCircles(rad=rates)
    #c.position()
    #circles = [c.circles[i][:2] for i in sorted(range(len(c.circles)), key=lambda k: c.circles[k][2], reverse=True)]
    #mx0, my0 = min([circ[0] for circ in circles]), min([circ[1] for circ in circles])
    #cent_sex = [(int(circ[0]),int(circ[1]-my0+1)) for circ in circles]
    pos = posLookup[geo]
    cent_sex = [(-int(r/2) if i==1 else int(r/2), int(display_force.ChartWindow.SHIFT/5)) \
                 for i, r in enumerate(rates)]
    #cent_sex = [(int(r/2), 0) for i, r in enumerate(rates)]
    [d['positions'].update({'geo':{'x':pos['x'] + pos['offx'] - (cent_sex[i][0]),   \
                                   'y':pos['y'] - pos['offy'] - (cent_sex[i][1])}   \
                                    }) for i, d in enumerate(array)]
                                    
###############################################################################              
# prepare the charter for display of total changes

df_total = df[(df['sex']=='T')                          \
              & (df['age']==data.AGE_LABELS['TOTAL'])   \
              & ~(df['geo']==data.GEO_LABELS['EU28'])]
df_total['id'] = len(df_status) + len(df_total) - np.array(df_total['pc_pop']).argsort().argsort() - 1 
data_total = df_total.to_dict(orient="records")
[d.update({'positions': {'total':{'x':1200,                                                         \
                                  'y':np.int(50*d['change']) if ~np.isnan(d['change']) else 1.}   \
                        }                                                                           \
          }) for d in data_total]                           
[d.update({'positions': {'geo':{'x': d['positions']['total']['x'],      \
                                'y': d['positions']['total']['y']}      \
                        }                                               \
          }) for d in data_total]                           

# update output data
                         
data_status.extend(data_total)   
rate_data_status = json.dumps(data_status)
rate_data_status.replace('NaN','Infinity')

###############################################################################              
## OBSOLETE
## not used in proposed display
                              
## prepare data with all possible breakdowns

df_break = df[~(df['sex']=='T')                         \
              & ~(df['geo']==data.GEO_LABELS['EU28'])   \
              & ~(df['age']==data.AGE_LABELS['TOTAL'])]
df_break['id'] = len(df_break) - np.array(df_break['change']).argsort().argsort() - 1
data_break = df_break.to_dict(orient="records")

break_win = display_force.ChartWindow(domain=[0,4000])
 
rates_break = [np.int(break_win.rScale(d[TIME[1]]))      \
               if ~np.isnan(d[TIME[1]]) else 1.          \
                for d in data_break] 
                
t = display_force.PackedCircles(rad=rates_break)
t.position()
t.plot()
circles = [t.circles[i][:2]                             \
           for i in sorted(range(len(t.circles)), key=lambda k: t.circles[k][2], reverse=True)]
centre = sorted([(int(circ[0]),int(circ[1])) for circ in circles], key=lambda item: item[1],reverse=True)   
[d.update({'positions': {'total':{'x':break_win.centerX-centre[d['id']][0],   \
                                  'y':break_win.centerY-centre[d['id']][1]    \
                                  }                                             \
                        }                                                       \
          }) for d in data_break]

df_age = df[~(df['sex']=='T')                         \
              & (df['geo']==data.GEO_LABELS['EU28'])]
df_age['id'] = len(df_age) - np.array(df_age['change']).argsort().argsort() - 1
data_age = df_age.to_dict(orient="records")

df_age.drop(['sex', 'geo'], axis='columns', inplace=True)    

n_age_child     = (len(GEO)-1)*(len(SEX)-1) # -1: get rid of 'T'/'TOTAL' labels
cat_age_data = [{"label": data.AGE_LABELS[age], 
             "total": np.float(np.around(df_age[df_age['age']==age][TIME[1]].values, decimals=DECIMALS)),
             "num_children": n_age_child,
             "short_label": age
             } for age in AGE if age!='TOTAL']
cat_age_list = list([data.AGE_LABELS[age] for age in data.AGE_LABELS.keys() if age!='TOTAL'])    

age_win = display_force.ChartWindow(domain=[0,4000]) 

# (x,y) age positions for age table
posLookup = age_win.table_cells(AGE)
for age in AGE:
    if age=='Y_GE18' or age=='TOTAL': continue
    print('* group age category {}'.format(age))
    array_break = [d for d in data_age if d['age']==data.AGE_LABELS[age]]
    rates = [np.int(age_win.rScale(d[TIME[1]])) if ~np.isnan(d[TIME[1]]) else 1.  \
            for d in array_break]
    c = display_force.PackedCircles(rad=rates)
    c.position()
    circles = [c.circles[i][:2] for i in sorted(range(len(c.circles)), key=lambda k: c.circles[k][2], reverse=True)]
    mx0, my0 = min([circ[0] for circ in circles]), min([circ[1] for circ in circles])
    cent_break = [(int(circ[0]),int(circ[1]-my0+1)) for circ in circles]
    pos = posLookup[age]
    [d['positions'].update({'age':{'x':pos['x'] + pos['offx'] - cent_break[i][0],   \
                                   'y':pos['y'] - pos['offy'] -cent_break[i][1]}    \
                                    }) for i, d in enumerate(array_break)]
 
data_break.extend(data_age)   
data_break = json.dumps(data_break)
data_break.replace('NaN','Infinity')
