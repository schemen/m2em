#!/usr/bin/env python
import logging
import re
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
    var1 = soup.body.findAll(text=re.compile("Last Page \((..)\)"))
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
