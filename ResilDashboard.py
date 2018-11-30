#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 11:48:11 2018

@author: skoebric
"""
import os
from datetime import datetime
import requests
import zipfile
import io
import pandas as pd
import pickle
import html2text
import json
import numpy as np
import toyplot
import toyplot.html
import toyplot.browser
import toyplot.svg
from IPython.core.display import clear_output
import folium
import geopandas as gpd
from folium import FeatureGroup


us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
    } #add in territories

state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

with open(f'statecentroids.pickle', 'rb') as handle:
    statecentroids = pickle.load(handle)


def dsiredfmaker(dsiredict):
    dsireprograms = dsiredict['program.csv']
    
    dsirestates = dsiredict['state.csv']
    statesdict = pd.Series(dsirestates.name.values, index=dsirestates.id).to_dict()
    dsireprograms['State'] = dsireprograms['state_id'].map(statesdict)
    
    dsiresector = dsiredict['implementing_sector.csv']
    sectordict = pd.Series(dsiresector.name.values,index=dsiresector.id).to_dict()
    dsireprograms['Implementing Sector'] = dsireprograms['implementing_sector_id'].map(sectordict)
    
    dsirecategory = dsiredict['program_category.csv']
    categorydict = pd.Series(dsirecategory.name.values,index=dsirecategory.id).to_dict()
    dsireprograms['Program Category'] = dsireprograms['program_category_id'].map(categorydict)
    
    dsiretype = dsiredict['program_type.csv']
    typedict = pd.Series(dsiretype.name.values,index=dsiretype.id).to_dict()
    dsireprograms['Program Type'] = dsireprograms['program_type_id'].map(typedict)
    
    dsireenergycat = dsiredict['energy_category.csv']
    energycatdict = pd.Series(dsireenergycat.name.values,index=dsireenergycat.id).to_dict()
    dsireprogramtechnology = dsiredict['program_technology.csv']
    programtechnologydict = pd.Series(dsireprogramtechnology.technology_id.values,index=dsireprogramtechnology.program_id).to_dict()
    dsiretechnologycat = dsiredict['technology_category.csv']
    dsiretechnologycat['energy_category'] = dsiretechnologycat['energy_category_id'].map(energycatdict)
    energycatdict = pd.Series(dsiretechnologycat.energy_category.values,index=dsiretechnologycat.name).to_dict()
    technologycatdict = pd.Series(dsiretechnologycat.name.values,index=dsiretechnologycat.id).to_dict()
    dsiretechnology = dsiredict['technology.csv']
    dsiretechnology['technology_category'] = dsiretechnology['technology_category_id'].map(technologycatdict)
    technologydict = pd.Series(dsiretechnology.name.values,index=dsiretechnology.id).to_dict()
    technologycatdict = pd.Series(dsiretechnology.technology_category.values,index=dsiretechnology.id).to_dict()
    dsireprograms['technology_id'] = dsireprograms['id'].map(programtechnologydict)
    dsireprograms['Technology Type'] = dsireprograms['technology_id'].map(technologydict)
    dsireprograms['Technology Category'] = dsireprograms['technology_id'].map(technologycatdict)
    dsireprograms['Energy Category'] = dsireprograms['Technology Category'].map(energycatdict)
    
    dsireprograms = dsireprograms.dropna(subset = ['Energy Category'])
    dsireprograms = dsireprograms.loc[dsireprograms['published'] == 1]
    dsireprograms['End Date'] = dsireprograms['end_date'].fillna('2099-01-01 00:00:00')
    dsireprograms['End Date'] = pd.to_datetime(dsireprograms['End Date'])
    dsireprograms = dsireprograms.loc[dsireprograms['End Date'] > datetime.now()]
    
    
    dsireprogramcounty = dsiredict['program_county.csv']
    dsireprogramzip = dsiredict['program_zipcode.csv']
    dsireprogramcity = dsiredict['program_city.csv']
    dsirezip = dsiredict['zipcode.csv']
    
    dsireparameterset = dsiredict['parameter_set.csv']
    dsireparameters = dsiredict['parameter.csv']
    
    def programidgetter(row):
        programid_ = row['id']
        programiddf_ = dsireparameterset.loc[dsireparameterset['program_id'] == programid_]
        parameterset_ = list(programiddf_['id'])
        if len(parameterset_) > 0:
            parameterdf_ = dsireparameters.loc[dsireparameters['parameter_set_id'].isin(parameterset_)]
            parameterdf_.sort_values(by = ['units','amount'], ascending = [True,False], inplace = True)
            parameterdf_ = parameterdf_.dropna(subset = ['amount','units'])
            if len(parameterdf_) > 0:
                parameterdf_ = parameterdf_[0:1]
                amount = int(parameterdf_['amount'][0:1].item())
                units = parameterdf_['units'][0:1].item()
                parametertuples.append((programid_, amount, units))
    
    parametertuples = []
    dsireprograms.apply(programidgetter, axis = 1)
    parametertuples = [i for i in parametertuples if len(i) == 3]
    programamount = {i[0]:i[1] for i in parametertuples}
    programunits = {i[0]:i[2] for i in parametertuples}
    dsireprograms['Max Incentive'] = dsireprograms['id'].map(programamount)
    dsireprograms['Incentive Units'] = dsireprograms['id'].map(programunits)
    
    def zipcodegetter(row):
        programid = row['id']
        
        dfcounty_ = dsireprogramcounty.loc[dsireprogramcounty['program_id'] == programid]
        counties_ = list(dfcounty_['county_id'])
        zips_from_counties_ = list(dsirezip.loc[dsirezip['county_id'].isin(counties_)]['zipcode'])
        
        dfzip_ = dsireprogramzip.loc[dsireprogramzip['program_id'] == programid]
        zipids_ = list(dfzip_['zipcode_id'])
        zips_from_zipids_ = list(dsirezip.loc[dsirezip['id'].isin(zipids_)]['zipcode'])
        
        dfcity_ = dsireprogramcity.loc[dsireprogramcity['program_id'] == programid]
        cities_ = list(set(dfcity_['city_id']))
        zips_from_cities_ = list(dsirezip.loc[dsirezip['city_id'].isin(cities_)]['zipcode'])
        
        zipsout = list(set(zips_from_counties_ + zips_from_zipids_ + zips_from_cities_))
        return zipsout
    
    dsireprograms['zipcodes'] = dsireprograms.apply(zipcodegetter, axis = 1)
    
    def summarycleaner(row):
        summarylist = [row['summary'], row['name'], row['Technology Category'], row['Energy Category'],
                       row['Program Type'], row['Program Category'], row['Implementing Sector']]
        summaryin = ' '.join(summarylist)
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = True
        text_maker.bypass_tables = True
        text_maker.escape_snob = True
        text_maker.ignore_emphasis = True
        text = text_maker.handle(summaryin)
        return text.lower()
    dsireprograms['summary'] = dsireprograms.apply(summarycleaner, axis = 1)
    
    dsireprograms.rename(columns = {'name':'Program Name'}, inplace = True)
    return dsireprograms

def LocalNewDsireChecker():
    cwd = os.getcwd()
    siblings = os.listdir(cwd)
    
    for i in siblings:
        if 'dsire' in str(i):
            pklname = i.split('.')[0]
    
    dsiremonth = int(pklname.split('-')[-1])
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    
    if currentmonth != dsiremonth:
        print('DSIRE data is outdated, downloading new data...')
        newpklname = f'dsire-{currentyear}-{currentmonth}'
        dsirezipurl = f'https://ncsolarcen-prod.s3.amazonaws.com/fullexports/dsire-{currentyear}-{currentmonth}.zip'
        r = requests.get(dsirezipurl)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        zfiles = z.namelist()
        csvfiles = {}
        for file in zfiles:
            if file.endswith(".csv"):
                file_ = z.open(file)
                df_ = pd.read_csv(file_)
                csvfiles[file] = df_

        dsireprograms = dsiredfmaker(csvfiles)
        with open(f'{newpklname}.pickle', 'wb') as handle:
            pickle.dump(dsireprograms, handle, protocol=pickle.HIGHEST_PROTOCOL)
        os.remove(f'{pklname}.pickle') 
    else:
        print('current DSIRE data found...')
        with open(f'{pklname}.pickle', 'rb') as handle:
            csvfiles = pickle.load(handle)
        return csvfiles
    
def NewDsireChecker():
    cwd = os.getcwd()
    siblings = os.listdir(cwd)
    
    for i in siblings:
        if 'dsire' in str(i):
            pklname = i.split('.')[0]
    
    dsiremonth = int(pklname.split('-')[-1])
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    
    if currentmonth != dsiremonth:
        print('DSIRE data is outdated, downloading new data...')
        dsirezipurl = f'https://ncsolarcen-prod.s3.amazonaws.com/fullexports/dsire-{currentyear}-{currentmonth}.zip'
        r = requests.get(dsirezipurl)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        zfiles = z.namelist()
        csvfiles = {}
        for file in zfiles:
            if file.endswith(".csv"):
                file_ = z.open(file)
                df_ = pd.read_csv(file_)
                csvfiles[file] = df_
        print('current DSIRE data downloaded (but not commited!)')
        dsireprograms = dsiredfmaker(csvfiles)
        return dsireprograms
    else:
        print('current DSIRE data found...')
        with open(f'{pklname}.pickle', 'rb') as handle:
            dsireprograms = pickle.load(handle)
        return dsireprograms
    
    
def DsireFilterer(dsirefile, stateinput = '', zipinput = '', searchinput = ''):
    df = dsirefile.copy()
    dfstate = df.loc[df['State'] == stateinput]
    dfstate['zipTrue'] = False
    if zipinput != '':
        def zipsearcher(row):
            ziplist = row['zipcodes']
            if int(zipinput) in ziplist:
                return True
            else:
                return False
        dfstate['zipTrue'] = dfstate.apply(zipsearcher, axis = 1)
        dfzips = dfstate.loc[dfstate['zipTrue'] == True]
        dfstate = pd.concat([dfzips, dfstate])
        dfstate.drop(columns = ['zipTrue'], inplace = True)
        dfstate.drop_duplicates(subset = ['id'], keep = 'first', inplace = True)
    if searchinput != '':
        def searcher(row):
            searchstring = row['summary']
            searchterms = searchinput.split(' ')
            result = 0
            for t in searchterms:
                if t.lower() in searchstring:
                    result +=1
            if result == len(searchterms):
                return True
            else:
                return False
        dfstate['searchTrue'] = dfstate.apply(searcher, axis = 1)
        dfstate = dfstate.loc[dfstate['searchTrue'] == True]
    return dfstate

def requestmaker(api_url, source, zipcode = None, state = None, API_KEY = None, startdate = None):
    if source == 'NREL':
        if API_KEY == None:
            API_KEY = 'm064df9Oq0S0ssTkDOkyI6C5Vhn9nCwLVdwH6Aoy'
        if zipcode != None:
            url_ = f'https://developer.nrel.gov/api/{api_url}.json?api_key={API_KEY}&zip={zipcode}'
        elif (zipcode == None) & (state != None):
            url_ = f'https://developer.nrel.gov/api/{api_url}.json?api_key={API_KEY}&state_abbr={state}'
        response = requests.get(url_, verify = False)
    elif source =='openei':
        if API_KEY == None:
            API_KEY = 'jNj9M08NTFtyOs9Y1dtmcjuOWYnkMoATGHvNHwxD'
        url_= f'https://api.openei.org/{api_url}?version=5&format=json&api_key={API_KEY}&address={zipcode}&approved=true&detail=full'
        response = requests.get(url_, verify = False)
    elif source == 'EIA':
        if API_KEY == None:
            API_KEY = 'e29ec60601eaa48657d0571969d0830a'
        url_ = f'http://api.eia.gov/series/?api_key={API_KEY}&series_id={api_url}'
        response = requests.get(url_, verify = False)
    elif source == 'FEMA':
        now = datetime.now().date()
        yearago = now.replace(year = now.year - 1)
        yearagostring = str(yearago) + 'T04:00:00.000z'
        url_ = f"https://www.fema.gov/api/open/v1/{api_url}?$filter=declarationDate ge '{yearagostring}' and state eq '{state}'"
        response = requests.get(url_, verify = False)
    if response.ok:
        j = json.loads(response.content)
        return j
    else:
        response.raise_for_status()

def UtilityRatesPlotter(state):
    clear_output()
    state_abrev = us_state_abbrev[state]
    j_res = requestmaker(api_url = f'ELEC.PRICE.{state_abrev}-RES.A', source = 'EIA')['series'][0]['data']
    j_com = requestmaker(api_url = f'ELEC.PRICE.{state_abrev}-COM.A', source = 'EIA')['series'][0]['data']
    j_ind = requestmaker(api_url = f'ELEC.PRICE.{state_abrev}-IND.A', source = 'EIA')['series'][0]['data']
    s_res = pd.Series([i[1] for i in j_res], index = [i[0] for i in j_res])
    s_res.name = 'residential'
    s_com = pd.Series([i[1] for i in j_com], index = [i[0] for i in j_com])
    s_com.name = 'commercial'
    s_ind = pd.Series([i[1] for i in j_ind], index = [i[0] for i in j_ind])
    s_ind.name = 'industrial'
    df_ = pd.concat([s_res, s_com, s_ind], axis = 1).sort_index(ascending = True)[-10:]
    

    j_res_us = requestmaker(api_url = 'ELEC.PRICE.US-RES.A', source = 'EIA')['series'][0]['data']
    j_com_us = requestmaker(api_url = 'ELEC.PRICE.US-COM.A', source = 'EIA')['series'][0]['data']
    j_ind_us = requestmaker(api_url = 'ELEC.PRICE.US-IND.A', source = 'EIA')['series'][0]['data']
    s_res_us = pd.Series([i[1] for i in j_res_us], index = [i[0] for i in j_res_us])
    s_res_us.name = 'residential'
    s_com_us = pd.Series([i[1] for i in j_com_us], index = [i[0] for i in j_com_us])
    s_com_us.name = 'commercial'
    s_ind_us = pd.Series([i[1] for i in j_ind_us], index = [i[0] for i in j_ind_us])
    s_ind_us.name = 'industrial'
    df_us_ = pd.concat([s_res_us, s_com_us, s_ind_us], axis = 1).sort_index(ascending = True)[-10:]
    
    cp = toyplot.color.Palette()
    canvas = toyplot.Canvas(width = 550, height = 350, autorender = False)
    axes = canvas.cartesian(label = f'{state} Average Retail Electricity Price', ylabel = '$/kWh')
    
    label_style = {"text-anchor":"start", "-toyplot-anchor-shift":"3px"}
    
    state_res = axes.plot(df_.index, df_['residential'], style={"stroke":cp[0],
                                                                "stroke-width":2.5})
    axes.text(df_.index[-1],df_['residential'][-1], f"{state_abrev} Res.", color = cp[0], style = label_style)
    state_com = axes.plot(df_.index, df_['commercial'], style={"stroke":cp[1],
                                                                "stroke-width":2.5})
    axes.text(df_.index[-1],df_['commercial'][-1], f"{state_abrev} Com.", color = cp[1], style = label_style)
    state_ind = axes.plot(df_.index, df_['industrial'], style={"stroke":cp[2],
                                                                "stroke-width":2.5})
    axes.text(df_.index[-1],df_['industrial'][-1], f"{state_abrev} Ind.", color = cp[2], style = label_style)
    us_res = axes.plot(df_us_.index, df_us_['residential'], style={"stroke":cp[0],
                                                                "stroke-width":1})
    axes.text(df_us_.index[-1],df_us_['residential'][-1], f"US Res.", color = cp[0], style = label_style)
    us_com = axes.plot(df_us_.index, df_us_['commercial'], style={"stroke":cp[1],
                                                                "stroke-width":1})
    axes.text(df_us_.index[-1],df_us_['commercial'][-1], f"US Com.", color = cp[1], style = label_style)
    us_ind = axes.plot(df_us_.index, df_us_['industrial'], style={"stroke":cp[2],
                                                                "stroke-width":1})
    axes.text(df_us_.index[-1],df_us_['industrial'][-1], f"US Ind.", color = cp[2], style = label_style)
    axes.x.ticks.locator = toyplot.locator.Explicit(locations = df_.index)
    
    h = toyplot.html.tostring(canvas)
    return h
    
def ElectricityorGasPlotter(state, resource, zipcode = None):
    cp = toyplot.color.Palette()
    cpalpha = []
    for i in cp:
        i['a'] = 0.4
        cpalpha.append(i)
    colors = [cp[0],cpalpha[0],cp[1],cpalpha[1],cp[2],cpalpha[2]]
        
    if len(zipcode) != 5:
        zipcode = None
    if zipcode != None:
        j = requestmaker(api_url = 'cleap/v1/energy_expenditures_and_ghg_by_sector', source = 'NREL', zipcode = zipcode)
        geo = zipcode
    elif zipcode == None:
        state_abrev = us_state_abbrev[state]
        geo = state_abrev
        j = requestmaker(api_url = 'cleap/v1/energy_expenditures_and_ghg_by_sector', source = 'NREL', state = state_abrev)
    
    r = j['result'][list(j['result'].keys())[0]]
    labels = [f'{geo} Res.','US Res.', f'{geo} Com.', 'US Com.', f'{geo} Ind.', 'US Ind.']
    if resource == 'Elec':
        i_res_elec = r['residential']['elec_mwh'] / r['residential']['total_pop']
        i_com_elec = r['commercial']['elec_mwh'] / r['residential']['total_pop']
        i_ind_elec = r['industrial']['elec_mwh'] / r['residential']['total_pop']
        us_res_elec = 3.64
        us_com_elec = 3.29
        us_ind_elec = 2.62
        values_elec = [i_res_elec, us_res_elec, i_com_elec, us_com_elec, i_ind_elec, us_ind_elec]
        canvas_elec, axes_elec, mark_elec = toyplot.bars(values_elec, width=550, height=350, color = colors,
                                      label = f'{geo} Electricity Consumption Per Capita', ylabel = 'MWh')
        axes_elec.x.ticks.locator = toyplot.locator.Explicit(labels=labels)
        h_elec = toyplot.html.tostring(canvas_elec)
        return h_elec
              
    elif resource == 'Gas':
        i_res_gas = r['residential']['gas_mcf'] / r['residential']['total_pop']
        i_com_gas = r['commercial']['gas_mcf'] / r['residential']['total_pop']
        i_ind_gas = r['industrial']['gas_mcf'] / r['residential']['total_pop']
        us_res_gas = 15.42
        us_com_gas = 7.96
        us_ind_gas = 19.8
    
        values_gas = [i_res_gas, us_res_gas, i_com_gas, us_com_gas, i_ind_gas, us_ind_gas]
        canvas_gas, axes_gas, mark_gas = toyplot.bars(values_gas, width=550, height=350, color = colors,
                                          label = f'{geo} Natural Gas Consumption Per Capita', ylabel = 'MCF')
        axes_gas.x.ticks.locator = toyplot.locator.Explicit(labels=labels)
        h_gas = toyplot.html.tostring(canvas_gas)
        return h_gas

def ResourceMixPlotter(state):
    cp = toyplot.color.Palette()
    alt_cp = toyplot.color.brewer.palette("Accent")
    cpdict = {'Coal':alt_cp[7],
              'Natural Gas':cp[6],
              'Nuclear':cp[4],
              'Geothermal':cp[1],
              'Biomass':cp[3],
              'Wind':cp[0],
              'Solar':cp[5],
              'Hydro':cp[2],
              'Other':cp[7]}
    
    resources = {'Coal':'COW',
                 'Petroleum':'PEL',
                 'Natural Gas':'NG',
                 'Nuclear':'NUC',
                 'Hydro':'HYC',
                 'Geothermal':'GEO',
                 'Biomass':'WWW',
                 'Wind':'WND',
                 'Small-Scale PV':'DPV',
                 'PV':'SPV',
                 'CSP':'STH',
                 'Hydro PS':'HPS',
                 'Other Bio':'WAS',
                 'Other':'OTH',
                 'Other Gas':'OOG',
                 'Petroleum Coke':'PC'}
    state_abrev = us_state_abbrev[state]
    s_list = []
    for key, value in resources.items():
        j_ = requestmaker(api_url = f'ELEC.GEN.{value}-{state_abrev}-99.A', source = 'EIA')
        if 'series' in j_:
            r = j_['series'][0]['data']
            s_ = pd.Series([i[1] for i in r], index = [i[0] for i in r])
            s_.name = key
            s_list.append(s_)
    df = pd.concat(s_list, axis = 1)[-10:]
    otherlist = ['Petroleum Coke','Other Gas','Other Bio','Hydro PS','Petroleum', 'Small-Scale PV','PV','CSP']
    for l in otherlist:
        if l not in df.columns:
            df[l] = 0
    
    df['Other'] = df['Other'] + df['Other Gas'] + df['Petroleum Coke'] + df['Other Bio'] +df['Petroleum']
    df['Hydro'] = df['Hydro'] + df['Hydro PS']
    df['Solar'] = df['Small-Scale PV'] + df['PV'] + df['CSP']
    df.drop(axis = 'columns', labels = otherlist, inplace = True)
    df.dropna(how='all', inplace = True)
    df.fillna(0, inplace = True)
    df = df / 100
    df.sort_values(by = '2017', axis = 'columns', inplace = True, ascending = False)
    resourcelist = df.columns

    resourcecolorlist = [cpdict[i] for i in resourcelist]
    
    dfout = df.values
    canvas, axes, mark = toyplot.fill(dfout, width=550, height=350, color = resourcecolorlist, baseline = 'stacked',
                                      margin = (40,95,40,45), label = f'{state} Resource Generation Mix', ylabel = 'GWh')
    
    legendlist = []
    count = 0
    for i in resourcelist:
        l = (i, mark.markers[count])
        legendlist.append(l)
        count +=1
    legendlist = list(reversed(legendlist))
    canvas.legend(legendlist, corner = ("right", 50, 40, 200))
    axes.x.ticks.locator = toyplot.locator.Explicit(labels = df.index)
    h = toyplot.html.tostring(canvas)
    return h
    
def FEMADisasters(state):
    state_abrev = us_state_abbrev[state]
    state_fip = state_codes[state_abrev]
    j_dis = requestmaker(api_url = 'DisasterDeclarationsSummaries', source = 'FEMA', state = state_abrev)
    df_dis = pd.DataFrame(j_dis['DisasterDeclarationsSummaries'])
    df_dis.dropna(subset = ['placeCode'], inplace = True)
    df_dis['placeCode'] = [f'{state_fip}{str(i)[2:5]}'for i in df_dis['placeCode']]
    disastertypedict = {'DR':'Major Disaster Declaration',
                        'EM':'Emergency Declaration',
                        'FM':'Fire Management',
                        'FS':'Fire Suppression'}
    df_dis['disasterType'] = df_dis['disasterType'].map(disastertypedict)
    
    def titlemaker(row):
        dn = row['disasterNumber']
        dt = row['title']
        title = f'{dt.title()} ({dn})'
        return title
    df_dis['title'] = df_dis.apply(titlemaker, axis = 1)
    df_dis['title'] = [i.title() for i in df_dis['title']]
    return df_dis
    
def FEMAMapper(state, disaster_name, df_dis):
    state_abrev = us_state_abbrev[state]
    state_fip = state_codes[state_abrev]
    
    if disaster_name != 'All':
        df_dis_ = df_dis.loc[df_dis['title'] == disaster_name]
    else:
        df_dis_ = df_dis.copy()
    Countiesshpfile = "/Users/skoebric/Dropbox/shp files/cb_2017_us_county_20m/cb_2017_us_county_20m.shp"
    Countiesshp = gpd.read_file(Countiesshpfile)
    Countiesshp.crs = {'init': 'epsg:4326'}
    cshp = Countiesshp.loc[Countiesshp['STATEFP'] == state_fip]
    cshp['FIP'] = cshp['STATEFP'] + cshp['COUNTYFP']
    
    def geometryfinder(row):
        fip = row['placeCode']
        try:
            geo = cshp.loc[cshp['FIP'] == fip, 'geometry'].item()
            return geo
        except ValueError:
            return np.nan
    df_dis_['geometry'] = df_dis_.apply(geometryfinder, axis = 1)
    df_dis_.dropna(subset = ['geometry'], inplace = True)

    gdf_dis = gpd.GeoDataFrame(df_dis_, geometry = 'geometry')
    gdf_dis.crs = {'init': 'epsg:4326'}
    
    m = folium.Map(tiles = 'stamentoner', location = statecentroids[state_fip], zoom_start = 6,
                   max_zoom = 6, min_zoom = 2, width = 600, height = 400)
    
    ih_gdf_dis = gdf_dis.loc[gdf_dis['ihProgramDeclared'] == True]
    if len(ih_gdf_dis) > 0:
        ih_layer = FeatureGroup(name = 'Individual & Household Program', show = True)
        ih_geojson = folium.GeoJson(ih_gdf_dis, style_function = lambda x: {'fillColor': '#66C2A5',
                                                                        'fillOpacity':0.4,
                                                                        'color':'k',
                                                                        'opacity':0,
                                                                        'weight':0})
        ih_geojson.add_to(ih_layer)
        m.add_child(ih_layer)
    
    ia_gdf_dis = gdf_dis.loc[gdf_dis['iaProgramDeclared'] == True]
    if len(ia_gdf_dis) > 0:
        ia_layer = FeatureGroup(name = 'Individual Assistance', show = True)
        ia_geojson = folium.GeoJson(ia_gdf_dis, style_function = lambda x: {'fillColor': '#FC8D62',
                                                                        'fillOpacity':0.4,
                                                                        'color':'k',
                                                                        'opacity':0,
                                                                        'weight':0})
        ia_geojson.add_to(ia_layer)
        m.add_child(ia_layer)
        
    pa_gdf_dis = gdf_dis.loc[gdf_dis['paProgramDeclared'] == True]
    if len(pa_gdf_dis) > 0:
        pa_layer = FeatureGroup(name = 'Public Assistance', show = True)
        pa_geojson = folium.GeoJson(pa_gdf_dis, style_function = lambda x: {'fillColor': '#8DA0CB',
                                                                        'fillOpacity':0.4,
                                                                        'color':'k',
                                                                        'opacity':0,
                                                                        'weight':0})
        pa_geojson.add_to(pa_layer)
        m.add_child(pa_layer)
    
    hm_gdf_dis = gdf_dis.loc[gdf_dis['paProgramDeclared'] == True]
    if len(hm_gdf_dis) > 0:
        hm_layer = FeatureGroup(name = 'Hazard Mitigation Assistance', show = True)
        hm_geojson = folium.GeoJson(hm_gdf_dis, style_function = lambda x: {'fillColor': '#E78AC3',
                                                                        'fillOpacity':0.4,
                                                                        'color':'k',
                                                                        'opacity':0,
                                                                        'weight':0})
        hm_geojson.add_to(hm_layer)
        m.add_child(hm_layer)
        
    m.add_child(folium.map.LayerControl(collapsed = False, autoZIndex = True))
    return m._repr_html_()

