import logging
import ssl
import feedparser
import bin.m2emHelper as helper
from bin.models.m2emManga import Manga
from bin.M2emModels import *

# Remove verification need of feedparser
ssl._create_default_https_context = ssl._create_unverified_context


def RssParser(config):
    """ Function that handles the coordination of rss parsing """

    # Get all feeds
    db.get_conn()
    rssdata = Feeds.select().execute()

    logging.info("Checking for new Feed Data...")

    # loop through rss feeds
    for i in rssdata.iterator():

        # Parse feed and check entries
        logging.info("Getting Feeds for %s", i.url)
        try:
            feed = feedparser.parse(str(i.url))
        except Exception as identifier:
            logging.warning("Could not load feed: %s", identifier)

        for entry in feed.entries:
            current_manga = Manga()
            current_manga.load_from_feed(entry, str(feed.url))

            # No need to continue if it is already saved :)
            if not current_manga.duplicated.exists():
                current_manga.print_manga()
                current_manga.save()
