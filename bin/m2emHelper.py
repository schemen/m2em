#!/usr/bin/env python
import logging
import os
import sqlite3
import texttable
import requests
from bs4 import BeautifulSoup

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import bin.sourceparser.m2emMangastream as msparser

'''

    Helper Unit.
    This File provides functions to other classes


'''



'''
Function write a feed into the DB
Returns: N/A
'''
def writeFeed(url,database):
    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)
    # Insert Data
    try:
        c.execute("INSERT INTO feeds (url) VALUES (?)", (url,))
        conn.commit()
        print("Succesfully added \"%s\" to the List of RSS Feeds" % url)
    except Exception as e:
        logging.info("Failed to save feed into database: %s" % e)
    conn.close




'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printFeeds(database):

    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM feeds")
    __tabledata = __data.fetchall()

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_dtype(['i',  # int
                          't',])  # text
    table.header (["ID", "URL"])
    table.add_rows(__tabledata,header=False)
    print(table.draw())





'''
Function that gets feed data and display it nicely
Returns: tabledata
'''
def getFeeds(database):

    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM feeds")
    __tabledata = __data.fetchall()

    return __tabledata






'''
Function to decide sourceparser (Mangafox or Mangastream as of now)
Returns: SourceURL
'''
def getSourceURL(url):
    SourceURL = urlparse(url).netloc

    return SourceURL






'''
Function that gets Manga Data from Chapter URL
Returns: mangadata (array)
'''
def getMangaData(url):

    # Get source of to decide which parser to use
    origin = getSourceURL(url)

    # Mangastream Parser
    if origin == "mangastream.com":
  
        logging.info("Getting Mangadata from Mangastream.com for %s" % url)
      
        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame   = msparser.getTitle(page)
        pages       = msparser.getPages(page)
        chapter     = msparser.getChapter(url)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter]

    # Mangafox Parser
    elif origin == "mangafox.com":
        logging.info("Getting Mangadata from Mangafox.me")


    else:
        pass

    # Return mangadata
    return mangadata


'''
Function to create folders
'''
def createFolder(self):
    if not os.path.exists(self.path):
        os.makedirs(self.path)
        logging.debug("Folder Created!")
    else:
        logging.debug("Folder Exists!")
