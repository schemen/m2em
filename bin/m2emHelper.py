#!/usr/bin/env python
import logging
import datetime
import os
import sqlite3
import texttable
import requests
import validators
from urllib.parse import urlparse
import bin.sourceparser.m2emMangastream as msparser
import bin.sourceparser.m2emMangafox as mxparser

'''

    Helper Unit.
    This File provides functions to other classes


'''



'''
Create Database!
'''
def createDB(config):

    # get database name
    database = config["Database"]

    # Table Data
    sql_table_chapters  = """CREATE TABLE IF NOT EXISTS chapter (
                            chapterid	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            origin	TEXT,
                            title	TEXT NOT NULL,
                            date	TEXT,
                            url	TEXT NOT NULL,
                            desc	TEXT,
                            ispulled	INTEGER DEFAULT 0,
                            isconverted	INTEGER DEFAULT 0,
                            issent	INTEGER DEFAULT 0,
                            pages	INTEGER DEFAULT 0,
                            chapter	INTEGER DEFAULT 0,
                            manganame	TEXT);"""


    sql_table_users     = """CREATE TABLE IF NOT EXISTS user (
                            userid	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            Name	TEXT NOT NULL,
                            Email	TEXT,
                            kindle_mail	TEXT,
                            sendToKindle	INTEGER DEFAULT 0);"""

    sql_table_feeds     = """CREATE TABLE IF NOT EXISTS feeds (
                            feedid	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            url	TEXT NOT NULL);"""

    # Create DB
    try:
        conn = sqlite3.connect(database)
        logging.debug(sqlite3.version)
        c = conn.cursor()
        c.execute(sql_table_chapters)
        c.execute(sql_table_users)
        c.execute(sql_table_feeds)
    except Exception as e:
        logging.info(e)
    finally:
        conn.close()
        logging.info("Created database %s" % database)

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
        logging.info("Succesfully added \"%s\" to the List of RSS Feeds" % url)
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

    table = texttable.Texttable(max_width=120)
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_align(["l", "l", "l", "l", "l", "l"])
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't',
                          't'])  # text
    table.header (["ID", "MANGA", "CHAPTER", "CHAPTERNAME", "RSS ORIGIN", "SEND STATUS"])


    logging.info("Listing all chapters:")
    for row in __tabledata:
        # Rename row[8]
        if row[8] == 1:
            sendstatus = "SENT"
        else:
            sendstatus = "NOT SENT"
        table.add_row([row[0], row[11], row[10], row[5]+"\n", str(row[1]), sendstatus])
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



'''
Switch User Config sendToKindle from True to False and False to True
'''
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
Delete User!
'''
def deleteUser(userid, config):

    # Get database config
    database = config["Database"]


    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)

    # check if user exists
    __data = c.execute("select * from user where userid=(?)", (userid,))
    __userdata = __data.fetchone()

    # Delete user
    if not __userdata == None:
        try:
            c.execute("delete from user where userid=(?)", (userid,))
            conn.commit()
            logging.info("Deleted user with ID %s." % userid)
        except Exception as e:
            logging.info("Could not delete user! %s" % e)
    else:
        logging.info("User with ID %s does not exist!"% userid)

    c.close()




'''
Delete Chapter!
'''
def deleteChapter(chapterid, config):

    # Get database config
    database = config["Database"]


    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)

    # check if user exists
    __data = c.execute("select * from chapter where chapterid=(?)", (chapterid,))
    __chapterdata = __data.fetchone()

    # Delete user
    if not __chapterdata == None:
        try:
            c.execute("delete from chapter where chapterid=(?)", (chapterid,))
            conn.commit()
            logging.info("Deleted chapter with ID %s." % chapterid)
        except Exception as e:
            logging.info("Could not delete chapter! %s" % e)
    else:
        logging.info("Chapter with ID %s does not exist!"% chapterid)

    c.close()







'''
Delete Feed!
'''
def deleteFeed(feedid, config):

    # Get database config
    database = config["Database"]


    # Open Database
    try:
        conn = sqlite3.connect(database)
    except Exception as e:
        print("Could not connect to DB %s" % e)

    c = conn.cursor()
    logging.debug("Succesfully Connected to DB %s" % database)

    # check if user exists
    __data = c.execute("select * from feeds where feedid=(?)", (feedid,))
    __chapterdata = __data.fetchone()

    # Delete user
    if not __chapterdata == None:
        try:
            c.execute("delete from feeds where feedid=(?)", (feedid,))
            conn.commit()
            logging.info("Deleted feed with ID %s." % feedid)
        except Exception as e:
            logging.info("Could not delete feed! %s" % e)
    else:
        logging.info("Feed with ID %s does not exist!"% feedid)

    c.close()





'''
Switch Chapter Config issent from True to False and False to True
'''
def switchChapterSend(chapterid,config):

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
    __data = c.execute("select * from chapter where chapterid=(?)", (chapterid,))
    __chapterdata=__data.fetchone()


    if __chapterdata == None:
        logging.info("Chapter with this ID does not exist!")
    else:
        logging.debug("Chapter ID is %s" % __chapterdata[8])
        if __chapterdata[8] == 1:
            # Insert Data
            try:
                c.execute("update chapter set issent=0 where chapterid=(?)", (chapterid,))
                conn.commit()
                logging.info("Set status of \"%s\" as Not Sent!" % __chapterdata[2])
            except Exception as e:
                logging.debug("Failed to update status: %s" % e)
            conn.close
        else:
            # Insert Data
            try:
                c.execute("update chapter set issent=1 where chapterid=(?)", (chapterid,))
                conn.commit()
                logging.info("Set status of \"%s\" as Sent!" % __chapterdata[2])
            except Exception as e:
                logging.debug("Failed to update status: %s" % e)
            conn.close






'''
Function that prints the last 10 chapters
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

    #Cut the list down to max 10 articles
    __cuttabledata = __tabledata[:15]

    table = texttable.Texttable(max_width=120)
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_align(["l", "l", "l", "l", "l", "l"])
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't',
                          't'])  # text
    table.header (["ID", "MANGA", "CHAPTER", "CHAPTERNAME", "RSS ORIGIN", "SEND STATUS"])

    logging.info("Listing the last 10 chapters:")
    for row in __cuttabledata:
        # Rename row[8]
        if row[8] == 1:
            sendstatus = "SENT"
        else:
            sendstatus = "NOT SENT"
        table.add_row([row[0], row[11], row[10], row[5]+"\n", str(row[1]), sendstatus])

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
def getMangaData(url,entry):

    # Get source of to decide which parser to use
    origin = getSourceURL(url)

    print(origin)
    # Mangastream Parser
    if origin == "mangastream.com":

        logging.debug("Getting Mangadata from Mangastream.com for %s" % url)

        # Easy Stuff
        title = entry.title
        chapter_name = entry.description
        chapter_pubDate = entry.published

        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame   = msparser.getTitle(page)
        pages       = msparser.getPages(page)
        chapter     = msparser.getChapter(url)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter, title, chapter_name, chapter_pubDate]

    # Mangafox Parser
    elif origin == "mangafox.me":
        logging.debug("Getting Mangadata from Mangafox.me for %s" % url)

        # Easy Stuff
        title = entry.title
        chapter_pubDate = entry.published

        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame    = mxparser.getTitle(page)
        pages        = mxparser.getPages(page)
        chapter      = mxparser.getChapter(url)
        chapter_name = mxparser.getChapterName(page)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter, title, chapter_name, chapter_pubDate]


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


'''
Function that returns sanetized folder name
'''
def sanetizeName(name):
    if ":" in name:
        name = name.replace(":", "_")
        return name
    else:
        return name




'''
Check if time is older than 24h
Returns: true or false
'''
def checkTime(time):
    objecttime = datetime.datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z")
    now = datetime.datetime.now(datetime.timezone.utc)

    delta = now - objecttime

    if delta.days == 0:
        return True
    else:
        return False


'''

Init Logging!

'''
def initialize_logger(output_dir, outputlevel):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
     
    # create console handler and set level to info
    handler = logging.StreamHandler()
    if outputlevel == "debug":
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
    else:
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
 
    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s; %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
 
    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "all.log"))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s; %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

      # create debug file handler and set level to debug - per run 1 file
    handler = logging.FileHandler(os.path.join(output_dir, "run.log"), "w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s; %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)