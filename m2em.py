#!/usr/bin/env python
import logging
import validators
import argparse
import configparser
# Start of the fun!
import bin.m2emHelper as helper
import bin.m2emRssParser as mparser

def main():

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

    parser.add_argument("-v", "--verbose", help="Increase output verbosity",
                            action="store_true")
    parser.add_argument("-d", "--debug", help="Debug Mode",
                            action="store_true")
    args = parser.parse_args()


    # Logging
    if args.verbose:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # Read Config
    logging.debug("Loading configuration")
    config = configparser.ConfigParser()
    config.read("config.ini")
    configdata = config["CONFIG"]

    # Load Config Variables
    savelocation = configdata["SaveLocation"]
    ebookformat  = configdata["EbookFormat"]
    database     = configdata["Database"]

    if savelocation:
        logging.debug("Succesfully loaded SaveLocation: %s ", savelocation)
    if ebookformat:
        logging.debug("Succesfully loaded EbookFormat: %s ", ebookformat)
    if database:
        logging.debug("Succesfully loaded Database: %s ", database)

    '''    
    Catch -r/--add-rss
    '''
    if args.rss_feed:
        logging.info("Entered URL: %s" % args.rss_feed)
        if validators.url(args.rss_feed):
            helper.writeFeed(args.rss_feed,database)
        else:
            print("You need to enter an URL!")


    '''    
    Catch --list-feeds
    '''
    if args.list_feeds:
        # helper.printFeeds(database)
        mparser.RssParser(helper.getFeeds(database))

# Execute Main
if __name__ == '__main__':
    main()
