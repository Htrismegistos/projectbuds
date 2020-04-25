from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import pandas as pd
import numpy as np
sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=10, minute =56)


def scheduled_job():
    
	
    
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
    
    sick = infect('global_confirmed.csv')
    dead = infect('global_dead.csv')
    dead.columns = [i+'_dead' for i in dead.columns]
    
    final = pd.concat((sick,dead), axis = 1) 
    final.to_csv('final_data.csv')

sched.start()

