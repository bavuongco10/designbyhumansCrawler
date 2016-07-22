# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 20:59:14 2016

@author: VuGoN
"""


import workerpool
import requests
import os
import sys
from bs4 import BeautifulSoup
import re
import urlparse
#http://www.designbyhumans.com/shop/womens-t-shirts/
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
def getDataOriginal(img):
    return str(img.get('data-original'))

#result = requests.get('http://www.designbyhumans.com/shop/womens-t-shirts/?av=artwork')
#soup=BeautifulSoup(result.content,"html.parser")
#imgs = [getDataOriginal(img) for img in soup.find_all('img') if getDataOriginal(img) != 'None' and 'product' in getDataOriginal(img) ]
#r = requests.get('http://cdn4.designbyhumans.com/product/design/u1075178/pr275372-2-2789974-1000x1000-b-p-000000.png')
#with open("pr275372-2-2789974-9999x9999-b-p-000000.png", "wb") as code:
#    code.write(r.content)
#pages  = [int(x.getText()) for x in soup.find_all('a', {'class' :'page' }) if x.getText() != '']
#lastPage = max(pages)

# input :http://cdn4.designbyhumans.com/product/design/u1075178/pr275372-2-2789974-153x56-b-p-000000.jpg
# expected : http://cdn4.designbyhumans.com/product/design/u1075178/pr275372-2-2789974-1000x1000-b-p-000000.png
def getInfor(url):
    parts = url.split('/')
    if isInt(parts[-2]):
        pageNumber = parts[-2]
        subName = parts[-4]
    else:
        pageNumber = 1
        subName  = parts[-2]
    return {'pageNumber': pageNumber, 'subName' : subName }
    
def parseHTML(url):
    result = requests.get(url)
    soup=BeautifulSoup(result.content,"html.parser")
    return soup

def getLegitUrl(url,width,height):
    url = re.sub('\d+x\d+',''.join([str(width),'x',str(height)]),url)
    headResult = requests.head(url)
    if headResult.ok: 
        return url
    else:
        return headResult.ok
        
def getDownloadableUrl(url):
    url = url.replace('.jpg','.png')
    for i in [5000,2000,1000]:
        if(getLegitUrl(url,i,i)):
            return getLegitUrl(url,i,i)
    for j in list(reversed(range(0,1000,100))):
        if(getLegitUrl(url,j,j)):
            return getLegitUrl(url,j,j)

def savePNGToLocal(url,fileName):
    r = requests.get(url)
    with open(fileName, "wb") as code:
        code.write(r.content)

def getImageUrl(soup):
    imgs = [getDataOriginal(img) for img in soup.find_all('img') if getDataOriginal(img) != 'None' and 'product' in getDataOriginal(img)]
    return imgs;
    
def getLastPageNumber(soup):
    pages  = [int(x.getText()) for x in soup.find_all('a', {'class' :'page' }) if x.getText() != '']
    lastPage = max(pages)
    return lastPage

def setDir(directory = 'image'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    
def getImagesJob(url):
    soup = parseHTML(url)
    imgUrls = getImageUrl(soup);
    infor = getInfor(url)
    for u in imgUrls:
        data.append( {'url' : u, 'subName': infor['subName']} )
    
def dowloadImagesJob(data):
    try:
        url = data['url']
        subName = data['subName']
        url = getDownloadableUrl(url)
        fileName = '_'.join([ subName,url.split('/')[-1] ])
        savePNGToLocal(url,fileName)
        print fileName
    except:
        print data
        
def pool(job,params):
    print 'Initializing...'
    # Build our `map` parameters
    # Initialize a pool, 5 threads in this case
    pool = workerpool.WorkerPool(size=32)
    # The ``download`` method will be called with a line from the second 
    # parameter for each job.
    pool.map(job, params)
    # Send shutdown jobs to all threads, and wait until all the jobs have been completed
    pool.shutdown()
    pool.wait()
    print 'job well done!'

def standardizedUrl(url):
    url = url.replace('http://','')
    if len(re.findall('[/]\d*\S[/]',url)) == 0 :
        parts = url.split('/')
        length = len(parts)
        temp = parts[length-1]
        parts[length-1] = 'page'
        parts.append('1')
        parts.append(temp)
        return 'http://'+'/'.join(parts)
    return url;
     
#http://www.designbyhumans.com/shop/mens-t-shirts/page/1/?av=artwork

def crawlSubcategory(url):
    if '?av=artwork' not in url:
        raise ValueError('Url not contain ?av=artwork, go fuck yourself!...')
    url = standardizedUrl(url)
    soup = parseHTML(url)
    lastPage = getLastPageNumber(soup)
    pageUrls = [re.sub('[/]\d+[/]','/'+str(i)+'/',url) for i in range(1,lastPage+1)]
    print 'Begin get image urls job!'
    pool(getImagesJob,pageUrls)
    print 'Number of images:',len(data)
    setDir()
    print 'Begin download images job!'
    pool(dowloadImagesJob,data)
##################
#Test   
url = 'http://www.designbyhumans.com/shop/mens-t-shirts/?av=artwork'
data = []
crawlSubcategory(url)