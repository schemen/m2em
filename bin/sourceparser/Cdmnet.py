#!/usr/bin/env python
""" Cdmnet Parsing Module """
import logging
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

'''

        CDM Parser


'''


'''
get Manga Title
Returns: title
'''
def getTitle(page):
    title = None
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    search = re.search('<meta content="(.*?) -.*?property="og:title">', str(soup))
    try:
        title = search.group(1)
    except AttributeError:
        logging.error("No Title Fount!")

    return title


'''
get Manga Chapter name
Returns: Chapter name
'''
def getChapterName(page):

    logging.debug("CDM has no Chapternames")
    chaptername = ""
    return chaptername


'''
get Manga Pages
Returns: integer pages
'''
def getPages(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    search =re.search("var pages = \[.*'(.*?)',];", str(soup))
    pages = search.group(1)
    return pages



'''
get Manga chapter
Returns: integer chapter
'''
def getChapter(url):
    #soup = BeautifulSoup(page.content, 'html.parser')

    search = re.search('ler-online/(.*?)\Z', str(url))
    chapter = search.group(1)
    return chapter

'''
get Manga Pages URL
Returns: urllist
'''
def getPagesUrl(starturl,pages):
    pagesurllist=[]

    # Split URL to create list
    parsed = urlparse(starturl)

    # start url generator
    for page in range(pages):
        page = page + 1
        fullurl = parsed.scheme + "://" + parsed.netloc + parsed.path + "#" + str(page)
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
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get CDN URL suffix
    search =re.search("var urlSulfix = '(.*?)';", str(soup))
    cdnsuffix = search.group(1)

    # Get pagenumber 
    var = re.search('ler-online/.*?#(.*?)\Z', str(pageurl))
    pagenumber = var.group(1).zfill(2)


    imageurl = str(cdnsuffix + pagenumber + ".jpg")
    return imageurl
