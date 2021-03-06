# -*- coding: utf-8 -*-
    #urls
    
'''
url1a = 'https://ingatlan.com/szukites/elado+lakas+xi-ker+48-55-m2+ar-szerint?page='
url1b = 'https://ingatlan.com/szukites/elado+lakas+vi-ker+38-55-m2+ar-szerint?page='
url2 = 'https://ingatlanok.hu/elado/lakas/budapest-v-ker/25nm-tol;33nm-ig?page='
url2a = 'https://ingatlanok.hu/elado/lakas/budapest-xi-ker/48nm-tol;55nm-ig?page='
url2b = 'https://ingatlanok.hu/elado/lakas/budapest-vi-ker/38nm-tol;55nm-ig?page='
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
import certifi
import os

#multi-page
def _get_url(url, n):
    '''
    gets multipages session based webpages like search results specialized to ingatlan.com site
    
    url for URL
    n for number of pages to follow
    
    returns ads specific url in list
    '''
    urls = []
    link = url + str(n)
    print(link)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', \
                             ca_certs=certifi.where(), \
                            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'})
    response = http.request('GET', link)
    soup = BeautifulSoup(response.data, 'lxml')
    
    if 'https://ingatlan.com/' in link: 
        l = soup.find_all('div', attrs = {'class': 'listing js-listing listing--cluster-parent js-cluster-parent'})
        l = l + (soup.find_all('div', attrs = {'class': 'listing js-listing'}))
        for i in l:
            urls.append('https://ingatlan.com'+i.find('a')['href'])
            
    elif 'https://ingatlanok.hu/' in link:
        urls =[i['href'] for i in soup.find_all('a', attrs={'class': 'zi1'})]
    
    return urls

def _multipagesSearch(url , v=10):
    '''
    wrapper for _get_url(url, n) to introduce timer between page download 
    url for URL,
    v for number of pages to return
    
    _get_url:
    gets multipages session based webpages like search results specialized to ingatlan.com site
    
    returns all ad specific urls in list
    '''
    i=1
    while i <= v:
        onepage = _get_url(url, n=i)
        
        if 'allpages' in locals():
            allpages = allpages + onepage
        else: allpages = onepage
            
        time.sleep(1)
        i += 1
    return allpages

#one page
def _onepageSearch(url):
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

#compose for searchPage url retrieval
def searchPage(district):
    '''
    retrives the search page results ad's url into a [list] according to the given district.
    Options:
    District: 'V', 'VI','XI'
    '''
    
    if district == 'V':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+v-ker+25-33-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas/budapest-v-ker/25nm-tol;33nm-ig?page='
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest05-kerulet/hely-id:budapest05-kerulet,/netto-alapterulet:28~33/emelet:1,8'
    elif district == 'VI':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+vi-ker+38-55-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas/budapest-vi-ker/38nm-tol;55nm-ig?page='
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest06-kerulet/hely-id:budapest06-kerulet,/netto-alapterulet:38~55/emelet:1,8'
    elif district == 'XI':
        url1 = 'https://ingatlan.com/szukites/elado+lakas+xi-ker+48-55-m2+ar-szerint?page='
        url2 = 'https://ingatlanok.hu/elado/lakas/budapest-xi-ker/48nm-tol;55nm-ig?page='
        url3 = 'https://www.oc.hu/ingatlanok/lista/oldalszam:48/rendezes:relevance/felhasznalas:elado/jogi-status:hasznalt/tipus:flat/stilus:brick,/hely-ertek:budapest11-kerulet/hely-id:budapest11-kerulet,/netto-alapterulet:45~55/emelet:1,8'
    
    hu = _multipagesSearch(url2)
    if len(hu) == 0:
        text = 'ERROR IN RETRIEVAL'
    else:
        text = len(hu)
    print('Hu search: {}'.format(text))
    
    com = _multipagesSearch(url1)
    if len(com) == 0:
        text = 'ERROR IN RETRIEVAL'
    else:
        text = len(com)
    print('Com search: {}'.format(text))
    
    cen = _onepageSearch(url3)
    if len(cen) == 0:
        text = 'ERROR IN RETRIEVAL'
    else:
        text = len(cen)
    print('Cen search: {}'.format(text))
    
    alls = [*hu,*com,*cen]
    print('All urls: ', len(alls))
    
    alls =[i for i in alls if 'http' in i]
    return alls


#getting the ad body
def _get_body(url):
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
                body = _get_body(i)               
                txt = body.get_text()

                if 'Azonosító:' in txt:             
                    adshu.append(body)
                    
            except: pass
            
        elif 'oc.hu' in i:
            try:
                body = _get_body(i)               
                txt = body.get_text()
                
                if 'Regisztrációs szám:' in txt:             
                    adscen.append(body)
            except: pass
            
        else:
            try:
                body = _get_body(i)               
                txt = body.get_text()
                
                if 'Parkolás' in txt or 'Ingatlan állapota' in txt:             
                    adscom.append(body)
            except: pass
        
        n+=1 # counter
    
    now = dtime.datetime.now()
    m = [str(now.month) if len(str(now.month)) == 2 else '0' + str(now.month)]
    d = [str(now.day) if len(str(now.day)) == 2 else '0' + str(now.day)]
    y = str(now.year)
    
    with open('adshu'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adshu)
                file = 'adshu'+ district + '_' + d[0] + m[0] + y + '.csv'
                size = os.stat(file).st_size/(1024*1024)
                if size < 0.1:
                    print('ERROR IN SAVING adshu')
    with open('adscom'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adscom)
                file = 'adscom'+ district + '_' + d[0] + m[0] + y + '.csv'
                size = os.stat(file).st_size/(1024*1024)
                if size < 0.1:
                    print('ERROR IN SAVING adscom')
    with open('adscen'+ district + '_' + d[0] + m[0] + y + '.csv', 'w') as f:
                f.write('%s' % adscen)
                file = 'adscen'+ district + '_' + d[0] + m[0] + y + '.csv'
                size = os.stat(file).st_size/(1024*1024)
                if size < 0.1:
                    print('ERROR IN SAVING adscen')
    return 
    

#execute
for i in ['V','VI', 'XI']:
    urls = searchPage(i)
    with open('allurls.csv', 'w') as f:
    	f.write('%s' % urls)
    details(urls,i)
