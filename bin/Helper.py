#!/usr/bin/env python
import logging
import shutil
import datetime
import os
import texttable
import requests
import validators
from urllib.parse import urlparse
import bin.Config as Config
from bin.Models import *
import bin.sourceparser.Mangastream as msparser
import bin.sourceparser.Mangafox as mxparser
import bin.sourceparser.Cdmnet as cdmparser

'''

    Helper Unit.
    This File provides functions to other classes


'''

# Load config right at the start
config = None
if not config:
    config = Config.load_config()


'''
Create Database!
'''
def createDB():
    create_tables()

'''
Function set manga as sent
Returns: N/A
'''
def setIsSent(mangaid):

    try:
        # Open DB
        db.connection()
        query = Chapter.update(issent=1).where(Chapter.chapterid == mangaid)
        query.execute()
        logging.debug("Set chapter with ID %s as sent", mangaid)
    except  Exception as fail:
        logging.debug("Failed to save feed into database: %s", fail)




'''
Function write a feed into the DB
Returns: N/A
'''
def writeFeed(url):

    # Connect to DB
    db.connection()

    # Insert Data
    feed = Feeds.create(url=url)
    feed.save()
    logging.info("Succesfully added \"%s\" to the List of RSS Feeds", url)

    # Close connection
    db.close()

'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printFeeds():

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_dtype(['i',  # int
                          't',])  # text
    table.header(["ID", "URL"])

    # Connect
    db.connection()

    for row in Feeds.select():
        table.add_row([row.feedid, row.url])

    # Close connection
    db.close()

    logging.info(table.draw())

    
'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printUsers():

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't'])  # text
    table.header(["ID", "USERNAME", "EMAIL", "KINDLE EMAIL", "SEND EBOOK"])

    db.connection()
    for user in User.select():
        if user.sendtokindle == 1:
            sendstatus = "YES"
        else:
            sendstatus = "NO"
        table.add_row([user.userid, user.name, user.email, user.kindle_mail, sendstatus])
    db.close()
    logging.info(table.draw())



'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printChaptersAll():

    # Make the query
    db.connection()
    chapters = Chapter.select().order_by(Chapter.chapterid)
    db.close()

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
    for row in chapters:
        # Rename row[8]
        if row.issent == 1:
            sendstatus = "SENT"
        else:
            sendstatus = "NOT SENT"
        table.add_row([row.chapterid, row.manganame, row.chapter, row.title+"\n", str(row.origin), sendstatus])
    logging.info(table.draw())



'''
Function that creates user in an interactive shell
Returns: N/A
'''
def createUser():

    # Start interactive Shell!
    while True:
        username = input("Enter User Name: ")
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
        sendToKindle = "1"
    else:
        sendToKindle = "0"

    # Save data now!
    db.connection()
    newuser = User.create(email=email, name=username, sendtokindle=sendToKindle, kindle_mail=kindlemail)

    try:
        newuser.save()
    except IntegrityError as fail:
        db.rollback()
        logging.error(fail)
    finally:
        logging.info("Succesfully added user %s!", username)
    db.close()

'''
Switch User Config sendToKindle from True to False and False to True
'''
def switchUserSend(userid):

    user = ""

    # Get User
    db.connection()
    try:
        user = User.get(User.userid == userid)
    except DoesNotExist:
        logging.error("User does with ID %s does not exist!", userid)

    if user:
        logging.debug("User is %s", user.name)
        if user.sendtokindle == 1:
            # Insert Data
            try:
                user.sendtokindle = 0
                user.save()
                logging.info("Disabled Ebook sending on user %s", user.name)
            except Exception as e:
                logging.debug("Failed to user status: %s", e)
        else:
            # Insert Data
            try:
                user.sendtokindle = 1
                logging.info("Enabling Ebook sending on user %s", user.name)
                user.save()
            except Exception as e:
                logging.debug("Failed to user status: %s", e)
    
    db.close()


'''
Delete User!
'''
def deleteUser(userid):

    # Get User
    db.connection()

    try:
        user = User.get(User.userid == userid)
        user.delete_instance()
        logging.info("Deleted user %s.", user.name)
    except DoesNotExist:
        logging.info("User with ID %s does not exist!", userid)

    db.close()




'''
Delete Chapter!
'''
def deleteChapter(chapterid):

    # Get Chapter
    db.connection()

    try:
        chapter = Chapter.get(Chapter.chapterid == chapterid)
        chapter.delete_instance()
        logging.info("Deleted Chapter %s.", chapter.title)
    except DoesNotExist:
        logging.info("Chapter with ID %s does not exist!", chapterid)

    db.close()


'''
Delete Feed!
'''
def deleteFeed(feedid):

    # Get Feed
    db.connection()

    try:
        feed = Feeds.get(Feeds.feedid == feedid)
        feed.delete_instance()
        logging.info("Deleted Feed \"%s\".", feed.url)
    except DoesNotExist:
        logging.info("Feed with ID %s does not exist!", feedid)

    db.close()

'''
Function that prints the last 10 chapters
Returns: N/A
'''
def printChapters():

    # Make the query
    db.connection()
    chapters = Chapter.select().order_by(-Chapter.chapterid).limit(10)
    db.close()

    table = texttable.Texttable(max_width=120)
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_align(["l", "l", "l", "l", "l", "l"])
    table.set_cols_dtype(['i',  # int
                          't',
                          't',
                          't',
                          't',
                          't'])  # text
    table.header(["ID", "MANGA", "CHAPTER", "CHAPTERNAME", "RSS ORIGIN", "SEND STATUS"])

    logging.info("Listing the last 10 chapters:")
    for row in chapters:
        # Rename row[8]
        if row.issent == 1:
            sendstatus = "SENT"
        else:
            sendstatus = "NOT SENT"
        table.add_row([row.chapterid, row.manganame, row.chapter, row.title+"\n", str(row.origin), sendstatus])
    logging.info(table.draw())



'''
Function that gets feed data returns it
Returns: feeds
'''
def getFeeds():

    # Make the query
    db.connection()
    feeds = Feeds.select()
    db.close()

    return feeds



'''
Function that gets chapters and returns it
Returns: __chapterdata
'''
def getChapters():

    # Make the query
    db.connection()
    chapters = Chapter.select()

    return chapters


'''
Function that gets chapters from IDs and returns it
Returns: __chapterdata
'''
def getChaptersFromID(chapterids):


    chapterdata = []
    db.connection()

    for i in chapterids:
        # Get Data
        try:
            chapter = Chapter.select().where(Chapter.chapterid == i).get()
            chapterdata.append(chapter)
        except DoesNotExist:
            logging.error("Chapter with ID %s does not exist!", i)
            

    logging.debug("Passed chapters:")
    for i in chapterdata:
        logging.debug(i.title)
    return chapterdata



'''
Function that gets chapters and returns it
Returns: __userdata
'''
def getUsers():

    # Make the query
    db.connection()
    users = User.select()

    return users



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
def getMangaData(url, entry):

    # Get source of to decide which parser to use
    origin = getSourceURL(url)

    mangadata = []
    # Mangastream Parser
    if origin == "mangastream.com" or origin == "readms.net":

        logging.debug("Getting Mangadata from Mangastream.com for %s" % url)

        # Easy Stuff
        title = entry.title
        chapter_name = entry.description
        chapter_pubDate = entry.published

        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame = msparser.getTitle(page)
        pages = msparser.getPages(page)
        chapter = msparser.getChapter(url)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter, title, chapter_name, chapter_pubDate]

    # Mangafox Parser
    elif origin == "mangafox.me" or origin == "mangafox.la" or origin == "fanfox.net":
        logging.debug("Getting Mangadata from Mangafox. for %s" % url)

        # Easy Stuff
        title = entry.title
        chapter_pubDate = entry.published

        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame = mxparser.getTitle(page)
        pages = mxparser.getPages(page)
        chapter = mxparser.getChapter(url)
        chapter_name = mxparser.getChapterName(page)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter, title, chapter_name, chapter_pubDate]

    # CDM Parser
    elif origin == "cdmnet.com.br":
        logging.debug("Getting Mangadata from CDM. for %s" % url)

        # Easy Stuff
        title = entry.title
        chapter_pubDate = entry.published

        # Load page once to hand it over to parser function
        logging.debug("Loading Page to gather data...")
        page = requests.get(url)

        # Getting the data
        manganame = cdmparser.getTitle(page)
        pages = cdmparser.getPages(page)
        chapter = cdmparser.getChapter(url)
        chapter_name = cdmparser.getChapterName(page)

        logging.debug("Mangadata succesfully loaded")

        mangadata = [manganame, pages, chapter, title, chapter_name, chapter_pubDate]
    else:
        logging.error("Not supportet origin!")

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
    # Some feeds don't deliver a timezone value, inject Zulu
    try:
        objecttime = datetime.datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        time = time + " +0000"
        objecttime = datetime.datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z")

    now = datetime.datetime.now(datetime.timezone.utc)

    delta = now - objecttime

    if delta.days == 0:
        return True
    else:
        return False



'''
Verify if chapter has been downloaded
Returns: true or false
'''
def verifyDownload(chapter):

    saveloc = config["SaveLocation"]
    mangapages = chapter.pages
    mangatitle = chapter.title
    manganame = chapter.manganame

    # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
    mangatitle = sanetizeName(mangatitle)
    manganame = sanetizeName(manganame)

    downloadfolder = str(saveloc + manganame + "/" + mangatitle + "/images")

    if not os.path.exists(downloadfolder):
        return False
    else:
        # First check checks if there is the right amount of files in the folder
        if len(os.listdir(downloadfolder)) != int(mangapages):
            shutil.rmtree(downloadfolder)
            return False
        else:
            # second check checks if there is an unfinished download
            for item in os.listdir(downloadfolder):

                if item.endswith(".tmp"):
                    logging.debug("%s seems to be corrupted, removing all images for redownload"% mangatitle)
                    shutil.rmtree(downloadfolder)
                    return False
            return True



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

    if not os.path.isdir(output_dir):
        createFolder(output_dir)


    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s; %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "debug.log"))
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

      # create debug file handler and set level to info
    handler = logging.FileHandler(os.path.join(output_dir, "m2em.log"))
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s; %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)



'''
Function that gets feed data and display it nicely
Returns: N/A
'''
def printManga(args):


    if args.list_manga == "all":

        workdata = []
        # Get Data
        data = Chapter.select(Chapter.manganame)
        for i in data:
            workdata.append(i.manganame)
        tabledata = set(workdata)


        if tabledata:
            logging.info("Mangas with chapters in the database:")
            for i in tabledata:
                logging.info("* %s"% i)
    else:
        data = Chapter.select().where(Chapter.manganame == args.list_manga)

        if not data:
            logging.error("No Manga with that Name found!")
        else:
            # Reverse List to get newest first
            #__tabledata.reverse()

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


            logging.info("Listing all chapters of %s:"% args.list_manga)
            for row in data:
                # Rename row[8]
                if row.issent == 1:
                    sendstatus = "SENT"
                else:
                    sendstatus = "NOT SENT"
                table.add_row([row.chapterid, row.manganame, row.chapter, row.desc+"\n", str(row.origin), sendstatus])
            logging.info(table.draw())
