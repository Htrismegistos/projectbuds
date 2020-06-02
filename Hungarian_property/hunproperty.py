# -*- coding: utf-8 -*-
    #urls
    
'''
url1a = 'https://ingatlan.com/szukites/elado+lakas+xi-ker+48-55-m2+ar-szerint?page='
url1b = 'https://ingatlan.com/szukites/elado+lakas+vi-ker+38-55-m2+ar-szerint?page='
url2 = 'https://ingatlanok.hu/elado/lakas+haz/budapest-v-ker:25nm-tol;33nm-ig?record=0&num=100'
url2a = 'https://ingatlanok.hu/elado/lakas+haz/budapest-xi-ker:48nm-tol;55nm-ig?record=0&num=100'
url2b = 'https://ingatlanok.hu/elado/lakas+haz/budapest-vi-ker:38nm-tol;55nm-ig?record=0&num=100'
url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest05-kerulet/hely-id:budapest05-kerulet,/netto-alapterulet:28~33/emelet:1,8'
url3a = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest11-kerulet/hely-id:budapest11-kerulet,/netto-alapterulet:45~55/emelet:1,8'
url3b = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest06-kerulet/hely-id:budapest06-kerulet,/netto-alapterulet:38~55/emelet:1,8'

url1 = 'https://ingatlan.com/szukites/elado+lakas+v-ker+25-33-m2+ar-szerint?page='
url2 = 'https://ingatlanok.hu/elado/lakas+haz/budapest-v-ker:25nm-tol;33nm-ig?record=0&num=100'
url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest05-kerulet/hely-id:budapest05-kerulet,/netto-alapterulet:28~33/emelet:1,8'
'''  

# libraries
import requests
#from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import urllib3
import warnings
warnings.filterwarnings('ignore')
import datetime as dtime
import time
import pandas as pd

#ingatlan.com, multi-page
def _multi_get(url, n):
    '''
    gets multipages session based webpages like search results specialized to ingatlan.com site
    
    url for URL
    n for number of pages to follow
    
    returns ads specific url in list
    '''
    urls = []
    link = url + str(n)
    print(link)
    http = urllib3.PoolManager(headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'})
    response = http.request('GET', link)
    soup = BeautifulSoup(response.data, 'lxml')
    l = soup.find_all('div', attrs = {'class': 'listing js-listing listing--cluster-parent js-cluster-parent'})
    l = l + (soup.find_all('div', attrs = {'class': 'listing js-listing'}))
    for i in l:
            urls.append('https://ingatlan.com'+i.find('a')['href'])
    
    return urls

def _multipagesSearch(url , v=10):
    '''
    wrapper for _multi_get(url, n) to introduce timer between page download 
    url for URL,
    v for number of pages to return
    
    _multi_get:
    gets multipages session based webpages like search results specialized to ingatlan.com site
    
    returns ad specific url in list
    '''
    i=1
    while i <= v:
        text = _multi_get(url, n=i)
        
        if 'csvtext' in locals():
            csvtext = csvtext + text
        else: csvtext = text
            
        time.sleep(1)
        i += 1
    return csvtext

#ingatlanok.hu, oc.hu, one page
def _simpleSearch(url):
    '''
    gets simple one page website from the URL
    
    returns ad specific url for .hu and oc.hu pages
    '''
    r=requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'})
    
    page = BeautifulSoup(r.content, 'lxml')
    body = page.body
    url_list = []
    if 'ingatlanok.hu' in url:
        a = body.find_all('div', attrs={'class': 'result-row'})
        for i in a:
            url_list.append(i.find_all('a')[1]['href'])
    if 'oc.hu' in url:
        a = body.find_all('div', attrs={'class': 'estate-list-box'})
        for i in a:
            url_list.append('https://www.oc.hu'+i.find_all('a')[0]['href'])
    return url_list

#compose for searPage url retrieval
def searchPage(district):
    '''
    retrives the search page results ad's url into a [list] according to the given district.
    Options:
    District: 'V', 'VI','XI'
    '''
    if district == 'V':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+v-ker+25-33-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas+haz/budapest-v-ker:25nm-tol;33nm-ig?record=0&num=100'
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest05-kerulet/hely-id:budapest05-kerulet,/netto-alapterulet:28~33/emelet:1,8'
    elif district == 'VI':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+vi-ker+38-55-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas+haz/budapest-vi-ker:38nm-tol;55nm-ig?record=0&num=100'
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest06-kerulet/hely-id:budapest06-kerulet,/netto-alapterulet:38~55/emelet:1,8'
    elif district == 'XI':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+xi-ker+48-55-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas+haz/budapest-xi-ker:48nm-tol;55nm-ig?record=0&num=100'
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest11-kerulet/hely-id:budapest11-kerulet,/netto-alapterulet:45~55/emelet:1,8'
    
    hu = _simpleSearch(url2)
    print('Hu search: ',len(hu))
    
    com = _multipagesSearch(url1)
    print('Com search: ',len(com))
    
    cen = _simpleSearch(url3)
    print('Cen search: ',len(cen))
    
    alls = [*hu,*com,*cen]
    print('All urls: ', len(alls))
    
    alls =[i for i in alls if 'http' in i]
    return alls

def _simple(url):
    '''
    Returns the page <body> tag from url retrieval
    '''
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'})
    body = BeautifulSoup(page.content, 'lxml').body

    return body

def details(urls, district):
    '''
    Go through the list of urls, retrieves the body tag. 
    Sorted by url, saves the body tag of those that has the keyword specific to the url source 
    
    district: 'V', 'VI', 'XI'
    '''
    
    adshu = []
    adscom = []
    adscen = []
    n=0
    for i in urls:
        print(n,'\t',i)
        if 'ingatlanok.hu' in i:
            try:
                back = _simple(i)               
                txt = back.get_text()

                if 'Azonosító:' in txt:             
                    adshu.append(back)
                    
            except: pass
            
        elif 'oc.hu' in i:
            try:
                back = _simple(i)               
                txt = back.get_text()
                
                if 'Regisztrációs szám:' in txt:             
                    adscen.append(back)
            except: pass
            
        else:
            try:
                back = _simple(i)               
                txt = back.get_text()
                
                if 'Parkolás' in txt or 'Ingatlan állapota' in txt:             
                    adscom.append(back)
            except: pass
        
        n+=1 # counter
    
    now = dtime.datetime.now()
    m = [str(now.month) if len(str(now.month)) == 2 else '0' + str(now.month)]
    d = [str(now.day) if len(str(now.day)) == 2 else '0' + str(now.day)]
    y = str(now.year)
    
    with open('adshu'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adshu)
    with open('adscom'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adscom)
    with open('adscen'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adscen)
    return

#execute
for i in ['V','VI', 'XI']:
    urls = searchPage(i)
    with open('allurls.csv', 'w') as f:
    	f.write('%s' % urls)
    details(urls,i)
