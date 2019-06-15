""" RSS Parsing Module """
import logging
import ssl
import feedparser
import re
from bin.models.Manga import Manga
from bin.Models import *

# Remove verification need of feedparser
ssl._create_default_https_context = ssl._create_unverified_context


def RssParser():
    """ Function that handles the coordination of rss parsing """

    # Get all feeds
    db.connection()
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

                # Check if any filters are set, continue as usual if not.
                if Filter.select().exists():
                    filters = Filter.select().execute()
                    for filter_entry in filters.iterator():

                        # Save manga that match the filter
                        if re.search(filter_entry.filtervalue, current_manga.title):
                            current_manga.save()
                            current_manga.print_manga()
                else:
                    current_manga.save()
                    current_manga.print_manga()

