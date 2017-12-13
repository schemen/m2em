import logging
import ssl
import feedparser
import bin.m2emHelper as helper
from bin.models.m2emManga import Manga

# Remove verification need of feedparser
ssl._create_default_https_context = ssl._create_unverified_context


def RssParser(config):
    """ Function that handles the coordination of rss parsing """


    # Get database config
    database = config["Database"]

    # Get all feeds
    rssdata = helper.getFeeds(database)

    logging.info("Checking for new Feed Data...")

    # loop through rss feeds
    for i in rssdata:

        # Parse feed and check entries
        logging.info("Getting Feeds for %s", i[1])
        try:
            feed = feedparser.parse(str(i[1]))
        except Exception as identifier:
            logging.warning("Could not load feed: %s", identifier)

        for entry in feed.entries:
            current_manga = Manga()
            current_manga.database = database
            current_manga.load_from_feed(entry, str(i[1]))

            # No need to continue if it is already saved :)
            if not current_manga.duplicated:
                current_manga.print_manga()
                current_manga.save()
