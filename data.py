#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 14:37:24 2017

@author: gjacopo
"""

from __future__ import print_function

import warnings
from collections import OrderedDict

import requests

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
    #import pyjstat
    from pyjstat import pyjstat
except:
    warnings.warn("Package pyjstat not imported - Used for JSONSTAT format")
    
__GEO_LABELS  = [('EU28', 'European Union (28 countries)'),
               # ('EU27':, 'European Union (27 countries)'),
               # ('EA19', 'Euro area (19 countries)'),
               # ('EA18', 'Euro area (18 countries)'),
               # ('EU', 'European Union (EU6-1972, EU9-1980, EU10-1985, EU12-1994, EU15-2004, EU25-2006, EU27-2013, EU28)'),
               # ('EA', 'Euro area (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)'),
               ('AT', 'Austria'),
               ('BE', 'Belgium'),
               ('BG', 'Bulgaria'),
               ('CY', 'Cyprus'),
               ('CZ', 'Czech Republic'),
               ('DE', 'Germany (until 1990 former territory of the FRG)'),
               ('DK', 'Denmark'),
               ('EE', 'Estonia'),
               ('EL', 'Greece'),
               ('ES', 'Spain'),
               ('FI', 'Finland'),
               ('FR', 'France'),
               ('HR', 'Croatia'),
               ('HU', 'Hungary'),
               ('IE', 'Ireland'),
               ('IT', 'Italy'),
               ('LT', 'Lithuania'),
               ('LU', 'Luxembourg'),
               ('LV', 'Latvia'),
               ('MT', 'Malta'),
               ('NL', 'Netherlands'),
               ('PL', 'Poland'),
               ('PT', 'Portugal'),
               ('RO', 'Romania'),
               ('SE', 'Sweden'),
               ('SI', 'Slovenia'),
               ('SK', 'Slovakia'),
               ('UK', 'United Kingdom'),
               ('CH', 'Switzerland'),
               ('NO', 'Norway'),
               ('IS', 'Iceland'),
               ('MK', 'the Former Yugoslav Republic of Macedonia'),
               ('RS', 'Serbia'),
               ('TR', 'Turkey')]
GEO_LABELS  = OrderedDict(__GEO_LABELS)
                
__AGE_LABELS = [('TOTAL', 'Total population'),
                ('Y_LT6', 'Less than 6 years'),
                ('Y6-10', 'From 6 to 10 years'),
                ('Y11-15', 'From 11 to 15 years'),
                ('Y_LT16', 'Less than 16 years'),
                ('Y16-19', 'From 16 to 19 years'),
                ('Y16-24', 'From 16 to 24 years'),
                ('Y_GE18', '18 years or over'),
                ('Y18-24', 'From 18 to 24 years'),
                ('Y20-24', 'From 20 to 24 years'),
                ('Y25-29', 'From 25 to 29 years'),
                ('Y25-34', 'From 25 to 34 years'),
                ('Y25-49', 'From 25 to 49 years'),
                ('Y35-44', 'From 35 to 44'),
                ('Y45-54', 'From 45 to 54'),
                ('Y50-64', 'From 50 to 64 years'),
                ('Y55-64', 'From 55 to 64 years'),
                ('Y65-74', 'From 65 to 74 years'),
                ('Y_GE75', '75 years or over')
                ]
 
AGE_LABELS  = OrderedDict(__AGE_LABELS)

SEX_LABELS  = {'M': 'Males',
               'F': 'Females',
               'T': 'Total'}

UNIT_LABELS = {'THS_PER': 'Thousand persons',
               'PC_POP': 'Percentage of total population'
               }               

STATUS_LABELS = {'POP': 'Population',
                'EMP': 'Employed persons',
                'SAL': 'Employees',
                'NSAL': 'Employed persons except employees',
                'NEMP': 'Not employed persons',
                'UNE': 'Unemployed persons',
                'RET': 'Retired persons',
                'INAC_OTH': 'Other inactive persons'}
    
class EstatDataFrame(object):

    PROTOCOL        = "http"
    API_LANG        = "en"
    API_FMT         = "json"
    API_DOMAIN      = 'ec.europa.eu/eurostat/wdds'
    API_VERS        = 2.1
    API_URL         = "{}://{}/rest/data/v{}/{}/{}".format(
                  PROTOCOL, API_DOMAIN, API_VERS, API_FMT, API_LANG
                  )

    def __init__(self, **kwargs):
        self.__indicator = []
        self.__url = ""
        self.__response = None
        if kwargs == {}:
            return
        if 'indicator' in kwargs:
            self.__indicator = kwargs.pop('indicator')
        
    @property
    def indicator(self):
        return self.__indicator
        
    @property
    def url(self):
        return self.__url
        
    @property
    def response(self):
        return self.__response

    def build_url(self, **kwargs):
        url = "{}/{}?".format(EstatDataFrame.API_URL, self.indicator[0])
        #if 'geo' in kwargs:
        #    url = "{}geo={}&".format(url, kwargs.pop('geo', None))
        _izip_replicate = lambda d : [(k,i) if isinstance(d[k], (tuple,list))        \
                else (k, d[k]) for k in d for i in d[k]]
        #_no_replicate = lambda d : d.items()
        filters = '&'.join(['{k}={v}'.format(k=k, v=v) for (k, v) in _izip_replicate(kwargs)])
        try:
            self.__url = "{}{}".format(url, filters)
        except:
            pass
        return self.url
    
    def get_response(self):
        # request the URL
        session = requests.session()
        try:
            response = session.head(self.url)
            response.raise_for_status()
        except:
            raise IOError("ERROR: wrong request formulated")  
        else:
            print ("OK: status={}".format(response.status_code))
        # load the data
        try:    
            response = session.get(self.url)
        except:
            raise IOError('error retrieveing response from URL')    
        try:
            if EstatDataFrame.API_FMT == 'json':
                self.__response = response.json()
            elif EstatDataFrame.API_FMT == 'unicode':
                self.__response = response.text  
        except:
            pass
        return self.response
        
    def load_json(self, pivot=None, index=None, use_label=True):
        try:
            # pyjstat produces dataframe in stacked shape
            dataset = pyjstat.Dataset.read(self.url)
        except:
            raise IOError("Dataframe not created")
        df = dataset.write('dataframe')
        if use_label is True:
            for name in dataset['dimension']:
                dname = dataset['dimension'][name]['category']['label']
                df[name] = df[name].map(dict((v,k) for k,v in dname.items()))
        if pivot is None:
            return df
        if index is None:
            index = set(df.columns).difference({pivot}.union({'value'}))
            # or: index = [c for c in df.columns if c not in {pivot, 'ivalue'}]
        if PDVERS < 18:
            df = df.set_index(index + [pivot]).unstack(pivot)
        else:
            df = df.pivot_table(index=index, columns=pivot, values='value')
        df.reset_index(drop=False, inplace=True)    
        try:
            #df.index.name = None
            #df = df.reindex(df.index.rename(None)) 
            df.columns.name = None
        except:
            pass
        return df
        
    def __call__(self, **kwargs):
        # input data loading and formatting
        url = self.build_url(**kwargs)#analysis:ignore
        resp = self.get_response()#analysis:ignore
        df = self.load_json(pivot='time')
        return df  
