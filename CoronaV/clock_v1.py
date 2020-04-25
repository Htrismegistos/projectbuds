from apscheduler.schedulers.blocking import BlockingScheduler
import requests
sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=10, minute =56)

def scheduled_job():
    
	confirmed_global = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
	dead_global = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
	
	#list of sources
	pull = [confirmed_global,dead_global]
	save = ['time_series_covid19_confirmed_global.csv',\
	'time_series_covid19_deaths_global.csv']
	
	for p,s in zip(pull,save):
		r = requests.get(p).text

		with open(s, 'w') as f:
        		f.write(r)

sched.start()

