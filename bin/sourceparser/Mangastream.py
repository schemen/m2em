#!/usr/bin/env python
import logging
import re
import requests

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from bs4 import BeautifulSoup

'''

        MangaStream Parser


'''


'''
get Manga Title
Returns: title
'''
def getTitle(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    var = soup.findAll("span", {"class":"hidden-xs hidden-sm"})
    title = ''.join(var[0].findAll(text=True))

    return title


'''
get Manga Pages
Returns: integer pages
'''
def getPages(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    var1 = soup.body.findAll(text=re.compile("Last Page \((.*)\)"))
    pages = int(var1[0][11:-1])
    return pages



'''
get Manga chapter
Returns: integer chapter
'''
def getChapter(url):
    _var1 = urlparse(url).path
    _var2 = _var1.split("/")

    chapter = _var2[3]
    return chapter

'''
get Manga Pages URL
Returns: urllist
'''
def getPagesUrl(starturl,pages):
    pagesurllist=[]

    # Split URL to create list
    parsed = urlparse(starturl)

    # get url loc
    urlpath = parsed.path

    # start url generator
    for page in range(pages):
        page = page + 1
        urlpathsplit = urlpath.split("/")
        urlpathsplit[-1] = str(page)
        fullurllocation = "/".join(urlpathsplit)
        fullurl = parsed.scheme + "://" + parsed.netloc + fullurllocation
        pagesurllist.append(fullurl)

    logging.debug("All pages:")
    logging.debug(pagesurllist)
    return pagesurllist



'''
get Manga Image URL
Returns: urllist
'''
def getImageUrl(pageurl):
    # Download Page
    page = requests.get(pageurl)

    #Pass page to parser
    soup = BeautifulSoup(page.content, 'html.parser')
    var1 = soup.find(id='manga-page')

    imageurl = "https:" + var1['src']
    return imageurl
    pass