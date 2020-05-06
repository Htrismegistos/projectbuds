import pandas as pd
import numpy as np
import datetime as dt
import requests
import json
import warnings
warnings.filterwarnings('ignore')

from bokeh.plotting import figure
from bokeh.layouts import row, WidgetBox, column
from bokeh.models import HoverTool, Panel, NumeralTickFormatter, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Tabs, Select, RadioButtonGroup

def infect(source):
    '''
    Prepare base dataframe from csv. Add Wold count, null selection
    Returns timeindex and cols of countries saved as .csv
    '''
    df = pd.read_csv(source)
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
    
    #df.to_csv('clean_'+source, index= False)
    return df             
        
def make_data(selection_sum, norm = 0):
    '''
    Creates a column dataset based on interactive filter selection
    Returns ColumnDataSource.data.keys(): index, Date, Country, value
    '''
    
    # create list of column names form selection
    ##remove 'No selection' from the list if there are others selected
    if len(selection_sum) >1 :
        selection_sum = [i for i in selection_sum if i != 'No selection']
    else : selection_sum = selection_sum
        
    sel_daily = [i+'_daily' for i in list(set(selection_sum))]
    sel_dead = [i+'_dead' for i in selection_sum]
    sel_daily_dead = [i+'_dead' for i in sel_daily]

    df = sick[selection_sum + sel_daily + sel_dead+ sel_daily_dead]
    
    #normalise with 100.000 population
    if norm != 0:
        try:
            selection_sum.remove('No selection')
        except: None
        
        temp = pd.DataFrame()
        for i in selection_sum:
            
            n = (pop['data'][i])
            temp1 = df.loc[:,[ii for ii in df.columns if i in ii]] / (n)
            temp = pd.concat((temp, temp1), axis = 1) 
            #print(temp1)
            s_cds = temp
    else: s_cds = df.copy()
        
    s_cds.reset_index(inplace= True)

    s_cds['Date'] = pd.to_datetime(s_cds['Date'])

    #melts and combine sum values and diff values to a single df
    a1 = pd.melt(s_cds, id_vars = 'Date', value_vars = selection_sum, var_name = 'Country' )
    a2 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_daily, var_name = 'Country',value_name = 'value_day' )
    a3 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_dead, var_name = 'Country',value_name = 'value_dead' )
    a4 = pd.melt(s_cds, id_vars = 'Date', value_vars = sel_daily_dead, var_name = 'Country',value_name = 'value_day_dead' )
    s_cds = pd.concat([a1,a2['value_day'],a3['value_dead'],a4['value_day_dead']], axis = 1, ignore_index= True)
    s_cds.columns = ['Date', 'Country', 'value','value_day','value_dead','value_day_dead']
    
    #get rid of empty dates exept if 'No selection' is there
    s_cds = s_cds.applymap(lambda x: np.NaN if x == 0 else x)
    if 'No selection' not in s_cds['Country'].unique():
        s_cds.dropna(axis = 1, how = 'all', inplace = True)
          
    # colourise
    colour = {i : c for i,c in zip(s_cds['Country'].unique(),colour_list)}
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
    hover_fig2 = {'Date': '@Date{%Y-%m-%d}'
                     ,'Country': '@Country'
                    ,'Dead': '@value_dead{0}'}
    hover_fig3 = {'Date': '@Date{%Y-%m-%d}'
                     ,'Country': '@Country'
                    ,'Dead': '@value_day_dead{0}'}

    fig_kwargs = {
                  'plot_width': 700
                  ,'plot_height': 200
                  ,'x_axis_type': 'datetime'
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
                  }
    
    fig = figure(**fig_kwargs 
                ,title = 'Registered Infected'
                ,toolbar_location = 'above'
                ,tools = ['pan','wheel_zoom','box_zoom','box_select', 'reset'])
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
    fig2.add_tools(HoverTool(tooltips=hover_fig2,
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
    fig3.add_tools(HoverTool(tooltips=hover_fig3,
                            formatters ={'@Date': 'datetime', '@value_day_dead': 'numeral'},
                            mode = 'vline'))
    fig3.legend.location = 'top_left'
    fig3.yaxis.formatter=NumeralTickFormatter(format=",000,000") #format number display
    fig3.ygrid.band_fill_color="olive"  #creates band colouring
    fig3.ygrid.band_fill_alpha = 0.1                 
    
    

    layout1 =column(fig,fig1,fig2,fig3)
    layout2 =row(column(fig,fig1),column(fig2,fig3))
    return layout1,layout2

def update(attr, old, new):
    
    
    chkbox_act1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
    chkbox_act2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
    drpbox_act3 = [drop_box_group3.value]
    drpbox_act4 = [drop_box_group4.value]
    drpbox_act5 = [drop_box_group5.value]
    radiob_act6 = radiobuttgroup6.active
    print('Data type: {}'.format(radiob_act6))
    selection_sum = chkbox_act1+chkbox_act2+drpbox_act3+drpbox_act4+drpbox_act5
    
    selection_sum = list(set(selection_sum))
    print('Countries: {}'.format(selection_sum))
    new_src = make_data(selection_sum,radiob_act6)            
    src.data.update(new_src.data)

    return src
    
#data acquisition
sick = pd.read_csv('final_data.csv', index_col = 'Date')
pop = json.load(open('population_covid.json'))
col_list = [ i for i in sick.columns if 'dead' not in i and 'daily' not in i]
colour_list = ['#1f77b4','#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22','#17becf']

yesterday = dt.datetime.now().date() - dt.timedelta(days= 1)
if sick.iloc[-1,0] != dt.datetime.strftime(yesterday,'%m/%d/%y'):

    confirmed_global = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    dead_global = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

    #list of sources
    pull = [confirmed_global,dead_global]
    save = ['global_confirmed.csv',\
    'global_dead.csv']

    for p,s in zip(pull,save):
        r = requests.get(p).text
        with open(s, 'w') as f:
            f.write(r)

    conf = infect('global_confirmed.csv')
    dead = infect('global_dead.csv')
    dead.columns = [i+'_dead' for i in dead.columns]

    sick = pd.concat((conf,dead), axis = 1) 
    sick.to_csv('final_data.csv')


#make selection list excuding checkbox values
dropdown_list = ['No selection'] + [i for i in col_list \
                if i not in ['No selection', 'World', 'China', 'US', 'United Kingdom','Korea, South','Italy']]

checkbox_group1 = CheckboxGroup(labels=['World','China','US'], active=[0])
checkbox_group2 = CheckboxGroup(labels=['United Kingdom','Italy','Korea, South'], active= [0])
drop_box_group3 = Select(title="Select country",value='No selection',options=dropdown_list)
drop_box_group4 = Select(title="Select country",value='No selection',options=dropdown_list)
drop_box_group5 = Select(title="Select country",value='No selection',options=dropdown_list)
radiobuttgroup6 = RadioButtonGroup(labels=['Absolute', 'Normalized'], active=1)

start_sel1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
start_sel2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
start_sel3 = [drop_box_group3.value]
start_sel4 = [drop_box_group4.value]
start_sel5 = [drop_box_group5.value]
start_sel6 = radiobuttgroup6.active

checkbox_group1.on_change('active', update)
checkbox_group2.on_change('active', update)
drop_box_group3.on_change('value', update)
drop_box_group4.on_change('value', update)
drop_box_group5.on_change('value', update)
radiobuttgroup6.on_change('active', update)


ctrl1 = WidgetBox(checkbox_group1, sizing_mode = 'fixed', height= 80, width = 120) 
ctrl2 = WidgetBox(checkbox_group2, sizing_mode = 'fixed', height= 80, width = 120)
ctrl3 = WidgetBox(drop_box_group3, sizing_mode = 'fixed', height= 80, width = 120)
ctrl4 = WidgetBox(drop_box_group4, sizing_mode = 'fixed', height= 80, width = 120)
ctrl5 = WidgetBox(drop_box_group5, sizing_mode = 'fixed', height= 80, width = 120)
ctrl6 = WidgetBox(radiobuttgroup6, sizing_mode = 'fixed', height= 80, width = 120)

start_sum  = start_sel1 + start_sel2 +start_sel3 + start_sel4 + start_sel5 
src = make_data(start_sum, start_sel6)

fig = make_plot(src)

coLayout = column(row(ctrl1,ctrl2, ctrl3, ctrl4,ctrl5, ctrl6),fig[0])
roLayout = column(row(ctrl1,ctrl2, ctrl3, ctrl4,ctrl5, ctrl6),fig[1])
colPanel = Panel(child = coLayout, title = '1x4 Layout')
rowPanel = Panel(child = roLayout, title = '2x2 Layout')
tabs = Tabs(tabs=[colPanel,rowPanel])


curdoc().add_root(tabs)

