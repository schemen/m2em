#!/usr/bin/env python
import logging
import time
import argparse
import configparser
import datetime
import argcomplete
import validators
# Start of the fun!
import bin.m2emHelper as helper
import bin.m2emRssParser as mparser
import bin.m2emDownloader as mdownloader
import bin.m2emConverter as mconverter
import bin.m2emSender as msender

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
        parser.add_argument("--list-users", help="Lists all Users",
                                action="store_true")
        parser.add_argument("-s", "--switch-send", help="Pass ID of User. Switches said user Send eBook status")
        parser.add_argument("-S", "--switch-chapter", help="Pass ID of Chapter. Switches said Chapter Sent status")
        parser.add_argument("--daemon", help="Run as daemon",
                                action="store_true")
        parser.add_argument("-d", "--debug", help="Debug Mode",
                                action="store_true")
        argcomplete.autocomplete(parser)
        self.args = parser.parse_args()

        # Logging
        if self.args.debug:
            logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)


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
        if self.config["Sleep"]:
            logging.debug("Succesfully loaded Database: %s ", self.config["Sleep"])


    '''
    Catch -r/--add-rss
    '''
    def save_feed_to_db(self):
        logging.info("Entered URL: %s" % self.args.rss_feed)
        if validators.url(self.args.rss_feed):
            helper.writeFeed(self.args.rss_feed, self.config)
        else:
            logging.error("You need to enter an URL!")


    '''
    Catch -s/--switch-user
    '''
    def switch_user_status(self):
        logging.debug("Entered USERID: %s" % self.args.switch_send)
        helper.switchUserSend(self.args.switch_send, self.config)



    '''
    Catch -s/--switch-user
    '''
    def switch_chapter_status(self):
        logging.debug("Entered CHAPTERID: %s" % self.args.switch_chapter)
        helper.switchChapterSend(self.args.switch_chapter, self.config)




    '''    
    Catch --list-feeds
    '''
    def list_feeds(self):
        helper.printFeeds(self.config)


    '''    
    Catch -L/--list-chapters-all
    '''
    def list_all_chapters(self):
        helper.printChaptersAll(self.config)
        pass


    '''    
    Catch -l/--list-chapters
    '''
    def list_chapters(self):
        helper.printChapters(self.config)
        pass


    '''    
    Catch --list-users
    '''
    def list_users(self):
        helper.printUsers(self.config)
        pass



    '''    
    Catch -u/--add-user
    '''
    def add_user(self):
        helper.createUser(self.config)
        pass


    '''
    This are the worker, one round
    '''
    #  Worker to get and parse  rss feeds
    def parse_rss_feeds(self):
        mparser.RssParser(self.config)

    # Worker to fetch all images
    def images_fetcher(self):
        mdownloader.ChapterDownloader(self.config)

    # Worker to convert all downloaded chapters into ebooks
    def image_converter(self):
        mconverter.RecursiveConverter(self.config)

    # Worker to convert all downloaded chapters into ebooks
    def send_ebooks(self):
        msender.sendEbook(self.config)



    '''
    Application Run & Daemon loop
    '''
    def run(self):

        if self.args.rss_feed:
            self.save_feed_to_db()
            return

        if self.args.switch_send:
            self.switch_user_status()
            return

        if self.args.list_feeds:
            self.list_feeds()
            return

        if self.args.list_chapters_all:
            self.list_all_chapters()
            return

        if self.args.list_chapters:
            self.list_chapters()
            return

        if self.args.add_user:
            self.add_user()
            return

        if self.args.list_users:
            self.list_users()
            return


        if self.args.switch_chapter:
            self.switch_chapter_status()
            return


        # Mainloop
        loop = True
        while loop:
            if not self.args.daemon:
                loop = False

            logging.info("Starting Loop at %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            logging.info("Starting RSS Data Fetcher!")
            self.parse_rss_feeds()
            logging.info("Finished Loading RSS Data")

            logging.info("Starting all outstanding Chapter Downloads!")
            self.images_fetcher()
            logging.info("Finished all outstanding Chapter Downloads")

            logging.info("Starting recursive image conversion!")
            self.image_converter()
            logging.info("Finished recursive image conversion!")

            logging.info("Starting to send all ebooks!")
            self.send_ebooks()
            logging.info("Finished sending ebooks!")

            if loop:
                logging.info("Sleeping for %s seconds...\n" % (self.config["Sleep"]))
                time.sleep(int(self.config["Sleep"]))

# Execute Main
if __name__ == '__main__':
    me = M2em()
    me.run()
