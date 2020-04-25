import pandas as pd
import numpy as np
import datetime,datetime as dtt


def infect(source, *arg):
    '''
    Prepare base dataframe from csv. Add Wold count, null selection
    Returns timeindex and cols of countries
    '''

    df = pd.read_csv(s0)
    df.loc[df['Province/State'] == 'Hong Kong', 'Country/Region'] = 'Hong Kong*'
    df.loc[df['Province/State'] == 'Macau', 'Country/Region'] = 'Macau*'
    df.drop(['Lat','Long','Province/State'], axis = 1, inplace=True)
    
    # add World count
    df = df.append( pd.Series(['World'], index = ['Country/Region']).append(df.sum()[1:]), ignore_index =True)
    
    df = df.groupby('Country/Region').sum()   
    df = df.T
    
    #add Null selection
    df['No selection'] = np.NaN
    
    #calculate daily increase
    for i in df.columns:
        df[i+'_daily'] = df[[i]].diff(axis = 0, periods = 1)
    
    df.columns.name = 'Country'
    df.index.name = 'Date'

    return df

#notebook version top notch version
import warnings
warnings.filterwarnings('ignore')

from bokeh.io import show, curdoc
from bokeh.plotting import figure
from bokeh.layouts import row, WidgetBox, column
from bokeh.models import ColumnDataSource, WidgetBox
from bokeh.models import HoverTool, Panel, NumeralTickFormatter
from bokeh.models.widgets import CheckboxGroup, Tabs, Select
from bokeh.palettes import Set1

def make_data(selection_sum):
    '''
    Creates a column dataset based on interactive filter selection
    Returns ColumnDataSource.data.keys(): index, Date, Country, value
    '''
    
    # create list of column names form selection
    sel_country = list(set(selection_sum))
    sel_daily = [i+'_daily' for i in list(set(sel_country))]
    sel_dead = [i+'_dead' for i in sel_country]
    sel_daily_dead = [i+'_dead' for i in sel_daily]

    s_cds = sick[sel_country + sel_daily + sel_dead+ sel_daily_dead]
    s_cds.reset_index(inplace= True)

    s_cds['Date'] = pd.to_datetime(s_cds['Date'])

    #melts and combine sum values and diff values to a single df
    a1 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_country, var_name = 'Country' )
    a2 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_daily, var_name = 'Country',value_name = 'value_day' )
    a3 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_dead, var_name = 'Country',value_name = 'value_dead' )
    a4 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_daily_dead, var_name = 'Country',value_name = 'value_day_dead' )
    s_cds = pd.concat([a1,a2['value_day'],a3['value_dead'],a4['value_day_dead']], axis = 1, ignore_index= True)
    s_cds.columns = ['Date', 'Country', 'value','value_day','value_dead','value_day_dead']
    
    #get rid of empty dates
    s_cds = s_cds.applymap(lambda x: np.NaN if x == 0 else x)
    s_cds.dropna(axis = 1, how = 'all', inplace = True)
          
    # colourise
    colour = {i : c for i,c in zip(s_cds['Country'].unique(),Set1[9]) if i!= 'No selection'}
    colour['No selection'] = '#fafafa'
    s_cds['colour'] = s_cds['Country'].map(colour)
    
    return ColumnDataSource(s_cds)
def make_plot(src):
    '''
    Create plot according to fed in cds
    '''               
    hover_fig = {'Date': '@Date{%Y-%m-%d}'
                     ,'Country': '@Country'
                    ,'Infected': '@value{,000,000}'}
    hover_fig1 = {'Date': '@Date{%Y-%m-%d}'
                     ,'Country': '@Country'
                    ,'Infected': '@value_day{0}'}

    fig_kwargs = {
                  'plot_width': 700
                  ,'plot_height': 200
                  ,'x_axis_type': 'datetime'
                  ,'toolbar_location': 'above'
                  ,'tools': ['pan','wheel_zoom','box_zoom','box_select', 'reset']
                  ,'background_fill_color': '#f1f5fc'
                  ,'border_fill_color' : '#f1f5fc'

                  }
    plot_kwargs = {'source': src
                   ,'hover_fill_color':'red'
                   ,'hover_color':'red'
                   ,'hover_alpha': 1
                   ,'color' : 'colour'
                   ,'size': 6
                   ,'selection_color':'red'
                   ,'nonselection_color':'colour'
                   #,nonselection_alpha=0.3
                  }
    
    fig = figure(**fig_kwargs 
                ,title = 'Registered Infected')
    fig.diamond(x='Date',y='value', **plot_kwargs, legend='Country')
    
    fig.add_tools(HoverTool(tooltips=hover_fig,
                            formatters ={'@Date': 'datetime', '@value': 'numeral'},
                            mode = 'vline'))
    fig.legend.location = 'top_left'
    fig.yaxis.formatter=NumeralTickFormatter(format=",000,000") #format number display
    fig.ygrid.band_fill_color="olive"  #creates band colouring
    fig.ygrid.band_fill_alpha = 0.1
  ##################<<<<<<<<<<<<>>>>>>>>>>#################  
    fig1 = figure(**fig_kwargs
                 ,title = 'Daily increase')
    fig1.diamond(x='Date',y='value_day', **plot_kwargs)
    fig1.x_range = fig.x_range
    fig1.add_tools(HoverTool(tooltips=hover_fig1,
                            formatters ={'@Date': 'datetime', '@value_day': 'numeral'},
                            mode = 'vline'))
    fig1.legend.location = 'top_left'
    fig1.yaxis.formatter=NumeralTickFormatter(format=",000,000") #format number display
    fig1.ygrid.band_fill_color="olive"  #creates band colouring
    fig1.ygrid.band_fill_alpha = 0.1
  ##################<<<<<<<<<<<<>>>>>>>>>>#################  
    fig2 = figure(**fig_kwargs
                 ,title = 'Total dead')
    fig2.diamond(x='Date',y='value_dead', **plot_kwargs)
    fig2.x_range = fig.x_range
    fig2.add_tools(HoverTool(tooltips=hover_fig1,
                            formatters ={'@Date': 'datetime', '@value_dead': 'numeral'},
                            mode = 'vline'))
    fig2.legend.location = 'top_left'
    fig2.yaxis.formatter=NumeralTickFormatter(format=",000,000") #format number display
    fig2.ygrid.band_fill_color="olive"  #creates band colouring
    fig2.ygrid.band_fill_alpha = 0.1            
  ##################<<<<<<<<<<<<>>>>>>>>>>#################  
    fig3 = figure(**fig_kwargs
                 ,title = 'Daily increase dead')
    fig3.diamond(x='Date',y='value_day_dead', **plot_kwargs)
    fig3.x_range = fig.x_range
    fig3.add_tools(HoverTool(tooltips=hover_fig1,
                            formatters ={'@Date': 'datetime', '@value_day_dead': 'numeral'},
                            mode = 'vline'))
    fig3.legend.location = 'top_left'
    fig3.yaxis.formatter=NumeralTickFormatter(format=",000,000") #format number display
    fig3.ygrid.band_fill_color="olive"  #creates band colouring
    fig3.ygrid.band_fill_alpha = 0.1                 
    
    

    layout1 = (column(fig,fig1,fig2,fig3))
    layout2 =row(column(fig,fig1),column(fig2,fig3))
    return layout1,layout2

def update(attr, old, new):
    
    
    chkbox_actives1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
    chkbox_actives2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
    drpbox_actives3 = [drop_box_group3.value]
    drpbox_actives4 = [drop_box_group4.value]
           
    selection_sum = chkbox_actives1+chkbox_actives2+drpbox_actives3+drpbox_actives4

    new_src = make_data(selection_sum)            
    src.data.update(new_src.data)
    
    return src

#sourc declaration
sick = pd.read_csv('final_data.csv', index_col = 'Date')
col_list = [ i for i in sick.columns if 'dead' not in i and 'daily' not in i]

#make selection list without listing checkbox values
dropdown_list = ['No selection'] + [i for i in col_list \
                if i not in ['No selection', 'World', 'China', 'US', 'United Kingdom','Korea, South','Italy']]

checkbox_group1 = CheckboxGroup(labels=['World','China','US'], active=[0])
checkbox_group2 = CheckboxGroup(labels=['United Kingdom','Italy','Korea, South'], active= [0])
drop_box_group3 = Select(title="Select country",value='No selection',options=dropdown_list)
drop_box_group4 = Select(title="Select country",value='No selection',options=dropdown_list)

start_selection1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
start_selection2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
start_selection3 = [drop_box_group3.value]
start_selection4 = [drop_box_group4.value]

checkbox_group1.on_change('active', update)
checkbox_group2.on_change('active', update)
drop_box_group3.on_change('value', update)
drop_box_group4.on_change('value', update)


controls1 = WidgetBox(checkbox_group1, sizing_mode = 'fixed', height= 80, width = 120) 
controls2 = WidgetBox(checkbox_group2, sizing_mode = 'fixed', height= 80, width = 120)
controls3 = WidgetBox(drop_box_group3, sizing_mode = 'fixed', height= 80, width = 120)
controls4 = WidgetBox(drop_box_group4, sizing_mode = 'fixed', height= 80, width = 120)


start_sum  = start_selection1 + start_selection2 +start_selection3 + start_selection4 
src = make_data(start_sum)

fig = make_plot(src)

coLayout = column(row(controls1,controls2, controls3, controls4),fig[0])
roLayout = column(row(controls1,controls2, controls3, controls4),fig[1])
colPanel = Panel(child = coLayout, title = '1x4 Layout')
rowPanel = Panel(child = roLayout, title = '4x4 Layout')
tabs = Tabs(tabs=[colPanel,rowPanel])

curdoc().add_root(tabs)

