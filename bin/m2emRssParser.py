import logging
import feedparser
import bin.m2emHelper as helper
from bin.models.m2emManga import Manga


def RssParser(database):
    rssdata = helper.getFeeds(database)

    logging.info("Checking for new Feed Data...")
    # loop through rss feeds

    for i in rssdata:

        # Parse feed and check entries
        logging.info("Getting Feeds for %s" % i[1])
        feed = feedparser.parse(str(i[1]))

        for entry in feed.entries:
            current_manga = Manga()
            current_manga.database = database
            current_manga.load_from_feed(entry, str(i[1]))
            # current_manga.print()
            logging.info(current_manga)
            current_manga.save()
