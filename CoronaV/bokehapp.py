import pandas as pd
import numpy as np
import datetime,datetime as dtt


#import warnings
#warnings.filterwarnings('ignore')
from bokeh.models import ColumnarDataSource, WidgetBox, CheckboxGroup
from bokeh.layouts import row, WidgetBox, column
from bokeh.plotting import figure
from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Tabs, Select
from bokeh.palettes import Set1
from bokeh.io import curdoc


def infect(source, *arg):
    '''
    Prepare base dataframe from csv. Add Wold count, null selection
    
    '''
    df = pd.read_csv(s0)
    df.loc[df['Province/State'] == 'Hong Kong', 'Country/Region'] = 'Hong Kong*'
    df.loc[df['Province/State'] == 'Macau', 'Country/Region'] = 'Macau*'
    df.drop(['Lat','Long','Province/State'], axis = 1, inplace=True)
    # add World count
    df = df.append( pd.Series(['World'], index = ['Country/Region']).append(df.sum()[1:]), ignore_index =True)
    #add Null selection
    zeros = pd.Series(np.ones(len(df.columns[1:])), index = df.columns[1:])
    df = df.append(pd.Series(['No selection'], index = ['Country/Region']).append(zeros),ignore_index = True)
    
    df = df.groupby('Country/Region').sum()
    df = df.T
    df.columns.name = 'Country'
    df.index.name = 'Date'
 
    return df


def make_data(a,b,c,d):

    data_cds = pd.DataFrame()
    selection_sum = a+b+c+d
    print(selection_sum)
    s_cds = sick[selection_sum]
    s_cds.reset_index(inplace= True)
    s_cds.loc[:,'Date'] = pd.to_datetime(s_cds['Date'])
    s_cds = pd.melt(s_cds, id_vars= ['Date'], value_vars=s_cds.columns.to_list()[1:])
    s_cds = ColumnDataSource(s_cds)
    return s_cds

def make_plot(src):
    '''
    makes plots according to the view list


    hover_display = {'Date': '@gmDate{(%Y-%m-%d)}'}
    hover_display = """
    <div>Display</div
    <div>Team: @teamAbbr</div>
    <div><span>Win</span><span style='padding-left:40px; color: red'>@winLoss</span></div>

    '''
    
    
    colour_map = CategoricalColorMapper(factors = np.unique(src.data['Country']), palette = Set1[9])
    fig_kwargs = {'title' : 'Sick            '
                  ,'plot_width': 800
                  ,'plot_height': 200
                   ,'x_axis_type': 'datetime'
                  ,'tools': ['pan', 'zoom_in', 'zoom_out', 'reset', 'save']
                  }
    plot_kwargs = {'source': src
                   ,'width': 0.9
                   ,'fill_color': {'field': 'Country', 'transform': colour_map}
                  }

    fig = figure(**fig_kwargs)
    fig.vbar(x='Date',top='value', **plot_kwargs)
    #fig.add_tools(HoverTool(tooltips= hover_display))
    

    return fig

def update(attr, old, new):

    chkbox_actives1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
    chkbox_actives2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
    dropdown1_value = [dropdown1.value]
    dropdown2_value = [dropdown2.value]
    
    new_src = make_data(chkbox_actives1, chkbox_actives2, dropdown1_value,dropdown2_value)

    src.data.update(new_src.data)
    return src

s0 = 'time_series_covid19_confirmed_global.csv'
s1 = 'time_series_covid19_deaths_global.csv'
sick = infect(s0)


dropdown_list = ['No selection'] + [i for i in sick.columns.to_list() if i not in ['No selection','World','China','US','United Kingdom','Italy','Korea, South']]

checkbox_group1 = CheckboxGroup(
    labels=['No selection','World','China','US'], active=[0]) #list of checkbox limited
checkbox_group2 = CheckboxGroup(
    labels=['No selection','United Kingdom','Italy','Korea, South'], active= [1]) #list of checkbox limited
dropdown1 = Select(title="Select country",value='No selection',options=dropdown_list)
dropdown2 = Select(title="Select country",value='No selection',options=dropdown_list)


checkbox_group1.on_change('active', update)
checkbox_group2.on_change('active', update)
dropdown1.on_change('value', update)
dropdown2.on_change('value', update)

controls1 = WidgetBox(checkbox_group1, sizing_mode = 'fixed', height= 80, width = 150) 
controls2 = WidgetBox(checkbox_group2, sizing_mode = 'fixed', height= 80, width = 150)
controls3 = WidgetBox(dropdown1, sizing_mode = 'fixed', height= 50, width = 120)
controls4 = WidgetBox(dropdown2, sizing_mode = 'fixed', height= 50, width = 120)


start_selection1 = [checkbox_group1.labels[i] for i in checkbox_group1.active]
start_selection2 = [checkbox_group2.labels[i] for i in checkbox_group2.active]
dropdown1_start_value = [dropdown1.value]
dropdown2_start_value = [dropdown2.value]


src = make_data(start_selection1, start_selection2, dropdown1_start_value,dropdown2_start_value)

fig = make_plot(src)

layout = column(row(controls1,controls2, controls3, controls4),fig)
tab = Panel(child=layout, title = 'wins')
tabs = Tabs(tabs=[tab])

curdoc().add_root(tabs)