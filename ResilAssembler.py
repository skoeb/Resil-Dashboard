#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 14:11:58 2018

@author: skoebric
"""
import ipywidgets as widgets
import ResilDashboard
import warnings
import qgrid
warnings.filterwarnings("ignore")

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:85% !important; }</style>"))
display(HTML("<style>.output_wrapper, .output {height:auto !important; max-height:5000px;}.output_scroll {box-shadow:none !important; webkit-box-shadow:none !important;}</style>"))

style = {'description_width': '150px'}
layout = {'width': '300px'}

dsire = ResilDashboard.NewDsireChecker()
def dsirelinkapplier(row):
    id_ = row.id
    name_ = row['Program Name']
    link = f'<a href = "http://programs.dsireusa.org/system/program/detail/{id_}" target="_blank">{name_}</a>'
    return link

dsire['Program Name'] = dsire.apply(dsirelinkapplier, axis = 1)

states = sorted(list(set(dsire['State'])))

statewidget = widgets.Select(
                    options=states,
                    value='Florida',
                    rows = 12,
                    description='State:',
                    disabled=False,
                    style = style,
                    layout = {'width':'400px'})

zipwidget = widgets.Text(
                value = None,
                description='Zip Code (Optional):',
                disabled=False,
                style = style,
                layout = layout)

searchwidget = widgets.Text(
                    value = '',
                    description = 'Search Term (Optional):',
                    disabled = False,
                    style = style,
                    layout = layout)

disasterwidget = widgets.Select(
                    options = ['All'],
                    value = 'All',
                    rows = 5,
                    description = 'Disaster Name:',
                    disabled = False,
                    style = style,
                    layout = {'width':'400px'})

#global variable accessed by maprunner so we don't have to make two API calls. Could also be written as a class...
df_dis = ResilDashboard.FEMADisasters(statewidget.value)
def disasternamesgetter():
    global df_dis
    df_dis = ResilDashboard.FEMADisasters(statewidget.value)
    disaster_list = list(set(df_dis.title))
    disaster_list.append('All')
    disasterwidget.options = disaster_list
    disasterwidget.value = 'All'

def elecrunner(stateinput, zipinput):
    plot = ResilDashboard.ElectricityorGasPlotter(state = stateinput, zipcode = zipinput, resource = 'Elec')
    display(HTML(plot))
    
def gasrunner(stateinput, zipinput):
    plot = ResilDashboard.ElectricityorGasPlotter(state = stateinput, zipcode = zipinput, resource = 'Gas')
    display(HTML(plot))
    
def filterrunner(stateinput, zipinput, searchinput):
    grid = ResilDashboard.DsireFilterer(dsire, stateinput, zipinput, searchinput)
    grid.set_index('Program Name', inplace = True)
    grid = grid[['Implementing Sector','Program Category','Program Type','Technology Type', 'Energy Category']]
    col_options = {
        'width': 80,
    }
    col_defs = {
        'Program Name': {
            'width': 400,
        }
    }
    
    qgrid_widget = qgrid.show_grid(grid,
                                   column_options = col_options,
                                   column_definitions = col_defs,
                                   show_toolbar = False)
    disasternamesgetter()
    display(qgrid_widget)

def resourcemixrunner(stateinput):
    plot = ResilDashboard.ResourceMixPlotter(state = stateinput)
    display(HTML(plot))
    
def ratesrunner(stateinput):
    plot = ResilDashboard.UtilityRatesPlotter(state = stateinput)
    display(HTML(plot))
    
def maprunner(stateinput, disasterinput):
    html = ResilDashboard.FEMAMapper(state = stateinput, disaster_name = disasterinput, df_dis = df_dis)
    display(HTML(html))


grid_out = widgets.interactive_output(filterrunner, {'stateinput':statewidget,
                                               'zipinput':zipwidget,
                                               'searchinput':searchwidget})
            
rates_out = widgets.interactive_output(ratesrunner, {'stateinput':statewidget})

resource_out = widgets.interactive_output(resourcemixrunner, {'stateinput':statewidget})

elec_out = widgets.interactive_output(elecrunner, {'stateinput':statewidget,
                                                   'zipinput':zipwidget})
gas_out = widgets.interactive_output(gasrunner, {'stateinput':statewidget,
                                                  'zipinput':zipwidget})

map_out = widgets.interactive_output(maprunner, {'stateinput':statewidget,
                                                 'disasterinput':disasterwidget})


vbox1 = widgets.VBox([statewidget])
vbox2 = widgets.VBox([zipwidget,searchwidget, disasterwidget])
ui = widgets.HBox([vbox1,vbox2])
ui.justify_content = 'center'

cleap_ratesmix = widgets.HBox([resource_out, rates_out])
cleap_consumption = widgets.HBox([elec_out, gas_out])
cleap = widgets.VBox([cleap_ratesmix, cleap_consumption])
cleap.justify_content = 'center'
display(ui, grid_out, cleap, map_out)

  