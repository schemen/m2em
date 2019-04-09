#!/usr/bin/env python
""" Mangafox Parsing Module """
import logging
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import bin.Config as Config

'''

        MangaFox Parser


'''
# Splash Rendering Service address
config = Config.load_config()
splash_server = config["SplashServer"]

'''
get Manga Title
Returns: title
'''
def getTitle(page):
    title = None
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get Manga Titel
    search = re.search('content="Read\s(.*?)\smanga online,', str(soup))
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

    #Get Manga Titel
    search =re.search('var imagecount=(.*?);', str(soup))
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
    # Download Page

    # Splash LUA script
    script = """
    splash.resource_timeout = 5
    splash:add_cookie{"IsAdult", "1", "/", domain="fanfox.net"}
    splash:on_request(function(request)
        if string.find(request.url, "tenmanga.com") ~= nil then
            request.abort()
        end
    end)
    splash:go(args.url)
    return splash:html()
    """

    logging.debug("Sending rendering request to Splash")
    resp = requests.post(str(splash_server + "/run"), json={
        'lua_source': script,
        'url': pageurl
    })
    page = resp.content

    #Pass page to parser
    var =re.search('style=\"cursor:pointer\" src=\"//(.*?)\"', str(page))

    logging.debug(var.group(1))
    imageurl = "http://" + var.group(1)
    return imageurl
