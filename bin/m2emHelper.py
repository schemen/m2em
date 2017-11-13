#!/usr/bin/env python
import logging
import os
import sqlite3
import texttable
import requests
import validators

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
Function set manga as sent
Returns: N/A
'''
def setIsSent(mangaid, database):
    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)

    # Insert Data
    try:
        c.execute("update chapter set issent=1 where chapterid=(?)", (mangaid,))
        conn.commit()
        logging.debug("Set chapter with ID %s as sent" % mangaid)
    except Exception as e:
        logging.debug("Failed to save feed into database: %s" % e)
    conn.close






'''
Function write a feed into the DB
Returns: N/A
'''
def writeFeed(url,config):


    # Get database config
    database = config["Database"]


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
def printFeeds(config):


    # Get database config
    database = config["Database"]



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
    logging.info(table.draw())






'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printUsers(config):


    # Get database config
    database = config["Database"]



    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM user")
    __tabledata = __data.fetchall()

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't'])  # text
    table.header (["ID", "USERNAME", "EMAIL", "KINDLE EMAIL", "SEND EBOOK"])
    table.add_rows(__tabledata,header=False)
    logging.info(table.draw())







'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printChaptersAll(config):


    # Get database config
    database = config["Database"]



    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM chapter")
    __tabledata = __data.fetchall()

    # Reverse List to get newest first
    __tabledata.reverse()

    table = texttable.Texttable(max_width=150)
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_align(["l", "l", "l", "l", "l"])
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't'])  # text
    table.header (["ID", "MANGA", "CHAPTER", "CHAPTERNAME", "RSS ORIGIN"])

    logging.info("Listing all chapters:")
    for row in __tabledata:
        table.add_row([row[0], row[11], row[10], row[5]+"\n", str(row[1]), ])
    logging.info(table.draw())






'''
Function that creates user in an interactive shell
Returns: N/A
'''
def createUser(config):

    # Start interactive Shell!
    while True:
        username     = input("Enter User Name: ")
        if validators.truthy(username):
            break
        else:
            print("Please enter a valid username!")
            continue


    while True:
        email = input("Enter your Email: ")
        if validators.email(email):
            break
        else:
            print("Please enter a valid email!")
            continue

    while True:
        kindlemail = input("Enter your Kindle Email: ")
        if validators.email(kindlemail):
            break
        else:
            print("Please enter a valid Email!")
            continue

    while True:
        sendToKindle = input("Do you want to send Ebooks to this Account? [yes/no] ")
        if sendToKindle == "yes":
            break
        elif sendToKindle == "no":
            break
        else:
            print("Answer with yes or no.")
            continue

    logging.debug([username, email, kindlemail, sendToKindle])

    # switch sendToKindle to 0 or 1
    if sendToKindle == "yes":
        sendToKindle = "True"
    else:
        sendToKindle = "False"


    # Get database config
    database = config["Database"]


    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)
    # Insert Data
    try:
        c.execute("INSERT INTO user (Name, Email, kindle_mail, sendToKindle) VALUES (?,?,?,?)", (username,email,kindlemail,sendToKindle))
        conn.commit()
        print("Succesfully added \"%s\" to User" % username)
    except Exception as e:
        logging.info("Failed to save user into database: %s" % e)
    conn.close





def switchUserSend(userid,config):

    # Get database config
    database = config["Database"]


    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)

    # Get User
    __data = c.execute("select * from user where userid=(?)", (userid))
    __userdata = __data.fetchone()


    if __userdata == None:
        logging.info("User with this ID does not exist!")
    else:
        logging.debug("User is %s" % __userdata[4])
        if __userdata[4] == "True":
            # Insert Data
            try:
                c.execute("update user set sendToKindle='False' where userid=(?)", (userid,))
                conn.commit()
                logging.info("Disabled Ebook sending on user %s" % __userdata[1])
            except Exception as e:
                logging.debug("Failed to user status: %s" % e)
            conn.close
        else:
            # Insert Data
            try:
                c.execute("update user set sendToKindle='True' where userid=(?)", (userid,))
                conn.commit()
                logging.info("Enable Ebook sending on user %s" % __userdata[1])
            except Exception as e:
                logging.debug("Failed to user status: %s" % e)
            conn.close




'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printChapters(config):


    # Get database config
    database = config["Database"]



    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM chapter")
    __tabledata = __data.fetchall()

    # Reverse List to get newest first
    __tabledata.reverse()

    table = texttable.Texttable(max_width=150)
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_align(["l", "l", "l", "l", "l"])
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't'])  # text
    table.header (["ID", "MANGA", "CHAPTER", "CHAPTERNAME", "RSS ORIGIN"])

    logging.info("Listing the last 10 chapters:")
    for i in range(0,10):
        table.add_row([__tabledata[i][0], __tabledata[i][11], __tabledata[i][10], __tabledata[i][5]+"\n", str(__tabledata[i][1]), ])
    logging.info(table.draw())




'''
Function that gets feed data returns it
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
Function that gets chapters and returns it
Returns: __chapterdata
'''
def getChapters(database):

    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM chapter")
    __chapterdata = __data.fetchall()

    return __chapterdata







'''
Function that gets chapters and returns it
Returns: __userdata
'''
def getUsers(database):

    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)


    # Get Data
    __data = c.execute("SELECT * FROM user")
    __userdata = __data.fetchall()

    return __userdata






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
  
        logging.debug("Getting Mangadata from Mangastream.com for %s" % url)
      
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
def createFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.debug("Folder %s Created!" % folder)
    else:
        logging.debug("Folder %s Exists!" % folder)
