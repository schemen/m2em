#!/usr/bin/env python
import logging
import validators
import argparse
import configparser
import time
# Start of the fun!
import bin.m2emHelper as helper
import bin.m2emRssParser as mparser
import bin.m2emDownloader as mdownloader

#logging.basicConfig(format='%(message)s', level=logging.DEBUG)

class M2em:

    def __init__(self):

        # Get args right at the start
        self.args = None
        if not self.args:
            self.read_arguments()

        # Load config right at the start
        self.config = None
        if not self.config:
            self.read_config()


    def read_arguments(self):

        # Get user Input
        parser = argparse.ArgumentParser(description='Manga to eManga - m2em')
        parser.add_argument("-r", "--rss-feed", help="Add RSS Feed of Manga. Only Mangastream & MangaFox are supported")
        parser.add_argument("-u", "--add-user", help="Adds new user",
                                action="store_true")
        parser.add_argument("-l", "--list-chapters", help="Lists the last 10 Chapters",
                                action="store_true")
        parser.add_argument("-L", "--list-chapters-all", help="Lists all Chapters",
                                action="store_true")
        parser.add_argument("--list-feeds", help="Lists all feeds",
                                action="store_true")
        parser.add_argument("--daemon", help="Run as daemon",
                                action="store_true")

        parser.add_argument("-v", "--verbose", help="Increase output verbosity",
                                action="store_true")
        parser.add_argument("-d", "--debug", help="Debug Mode",
                                action="store_true")
        self.args = parser.parse_args()

        # Logging TODO, fix levels
        if self.args.verbose:
            logging.basicConfig(format='%(message)s', level=logging.INFO)
        if self.args.debug:
            logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


    #Read Config
    def read_config(self):

        logging.debug("Loading configuration")
        config_reader = configparser.ConfigParser()
        config_reader.read("config.ini")
        self.config = config_reader["CONFIG"]

        # Load Config Variables
        if self.config["SaveLocation"]:
            logging.debug("Succesfully loaded SaveLocation: %s ", self.config["SaveLocation"])
        if self.config["EbookFormat"]:
            logging.debug("Succesfully loaded EbookFormat: %s ", self.config["EbookFormat"])
        if self.config["Database"]:
            logging.debug("Succesfully loaded Database: %s ", self.config["Database"])



    def save_feed_to_db(self):

        '''
        Catch -r/--add-rss
        '''
        logging.info("Entered URL: %s" % self.args.rss_feed)
        if validators.url(self.args.rss_feed):
            helper.writeFeed(self.args.rss_feed, self.config)
        else:
            logging.error("You need to enter an URL!")

    def list_feeds(self):

        '''    
        Catch --list-feeds
        '''
        helper.printFeeds(self.config)



    # worker methods
    def parse_rss_feeds(self):

        return mparser.RssParser(self.config)

    def images_fetcher(self):
        # TODO Make code to fetch and sort images
        mdownloader(self.config)
        pass

    def image_converter(self):
        # TODO Convert images
        pass




    # Application Run & Daemon loop
    def run(self):

        if self.args.rss_feed:
            self.save_feed_to_db()
            return

        if self.args.list_feeds:
            self.list_feeds()
            return

        # Mainloop
        loop = True
        while loop:
            if not self.args.daemon:
                loop = False

            parsed_feeds = self.parse_rss_feeds()
            if parsed_feeds:
                self.images_fetcher(parsed_feeds)

            self.image_converter()

            if loop:
                logging.info("Sleeping for %s seconds" % (self.config["Sleep"]))
                time.sleep(int(self.config["Sleep"]))

# Execute Main
if __name__ == '__main__':
    me = M2em()
    me.run()
