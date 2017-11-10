#!/usr/bin/env python
import logging
import sqlite3
import feedparser
import bin.m2emHelper as helper


def RssParser(rssdata):

    print("Checking for new Feed Data...\n")
    # loop through rss feeds
    for i in rssdata:

        logging.info("Getting Feeds for %s" % i[1])
        
        
        # Parse feed and check entries
        feed = feedparser.parse(str(i[1]))

        for entry in feed.entries:
            
            # Assign Feed data variables
            article_title = entry.title
            chapter_link = entry.link
            chapter_pubDate = entry.published
            chapter_name = entry.description

            # Getting specific manga data
            logging.debug("Fetching Data from Weblink")
            mangadata = helper.getMangaData(chapter_link)

            logging.info("Finished Collecting Chapter Data!")

            manga_name      = mangadata[0]
            chapter_pages   = mangadata[1]
            chapter          = mangadata[2]

            print "Manga:         {}".format(manga_name)
            print "Chapter:       {}".format(chapter)
            print "Chapter Name:  {}".format(chapter_name) 
            print "Chapter Pages: {}".format(chapter_pages)           
            print "Released on:   {}".format(chapter_pubDate)
            print "URL:           {}".format(chapter_link)
            print "Parent feed:   {}".format(str(i[1]))
            print ""

            logging.info("Saving Chapter Data...")
            # Open Database
            try:
                conn = sqlite3.connect(database)
            except Exception as e:
                print("Could not connect to DB %s" % e)

            c = conn.cursor()
            logging.debug("Succesfully Connected to DB %s" % database)
