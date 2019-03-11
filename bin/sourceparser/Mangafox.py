#!/usr/bin/env python
""" Mangafox Parsing Module """
import logging
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

'''

        MangaFox Parser


'''


'''
get Manga Title
Returns: title
'''
def getTitle(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    #Get Manga Titel
    var = soup.find('meta', attrs=dict(name='og:description'))
    step1 = var.attrs['content']
    search = re.search('Read (.*?) manga online.*', step1)
    title = search.group(1)

    return title


'''
get Manga Chapter name
Returns: Chapter name
'''
def getChapterName(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    search = re.search(': (.*?) at MangaFox', str(soup))
    try:
        chaptername = search.group(1)
    except AttributeError:
        logging.debug("No Chapter name provided")
        chaptername = ""
    return chaptername


'''
get Manga Pages
Returns: integer pages
'''
def getPages(page):
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Total Page Count
    search = re.search('var imagecount=(.*?);', str(soup))
    pages = search.group(1)
    return pages



'''
get Manga chapter
Returns: integer chapter
'''
def getChapter(url):
    #soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    search = re.search('/c(.*?)/', str(url))
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

    # get url loc
    urlpath = parsed.path

    # start url generator
    for page in range(pages):
        page = page + 1
        urlpathsplit = urlpath.split("/")
        urlpathsplit[-1] = str(page)
        fullurllocation = "/".join(urlpathsplit)
        fullurl = parsed.scheme + "://" + parsed.netloc + fullurllocation + ".html"
        pagesurllist.append(fullurl)

    logging.debug("All pages:")
    logging.debug(pagesurllist)
    return pagesurllist



'''
get Manga Image URL
Returns: urllist
'''
def getImageUrl(pageurl):
    ff = webdriver.Firefox(options=options)

    # Download Page
    ff.get(pageurl)
    page_source = ff.page_source

    ff.quit()

    #Pass page to parser
    soup = BeautifulSoup(page_source, 'html.parser')
    var1 = soup.find('img', attrs={'class': 'reader-main-img'})

    imageurl = 'http://{}'.format(var1.attrs['src'].lstrip('/'))
    return imageurl
