import logging
import ssl
import feedparser
import bin.m2emHelper as helper
from bin.models.m2emManga import Manga

# Remove verification need of feedparser
ssl._create_default_https_context=ssl._create_unverified_context


def RssParser(config):


    # Get database config
    database = config["Database"]


    rssdata = helper.getFeeds(database)

    logging.info("Checking for new Feed Data...")
    # loop through rss feeds

    for i in rssdata:

        # Parse feed and check entries
        logging.info("Getting Feeds for %s" % i[1])
        try:
            feed = feedparser.parse(str(i[1]))
        except Exception as identifier:
            logging.warn("Could not load feed: %s" % identifier)
        feedparser.parse
       
        for entry in feed.entries:
            current_manga = Manga()
            current_manga.database = database
            current_manga.load_from_feed(entry, str(i[1]))
            current_manga.print_manga()
            current_manga.save()
