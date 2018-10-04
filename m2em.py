#!/usr/bin/env python
import os
import sys
import logging
import time
import argparse
import configparser
import datetime
import validators
from bin._version import __version__
# Start of the fun!
import bin.Helper as helper
import bin.RssParser as mparser
import bin.DownloaderHandler as mdownloader
import bin.ConverterHandler as mconverter
import bin.SenderHandler as msender

class M2em:
    """ Main Class """

    def __init__(self):

        # Python 3 is required!
        if sys.version_info[0] < 3:
            sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
            sys.exit(1)

        # Get args right at the start
        self.args = None
        if not self.args:
            self.read_arguments()


        # Load config right at the start
        self.config = None
        if not self.config:
            self.read_config()

        # Check if Database exists, else create
        if not os.path.isfile(self.config["Database"]):
            helper.createFolder(self.config["SaveLocation"])
            helper.createDB()


    def read_arguments(self):
        """ function that reads all arguments """

        # Get user Input
        parser = argparse.ArgumentParser(description='Manga to eManga - m2em')
        parser.add_argument("-af", "--add-feed",
                            help="Add RSS Feed of Manga. Only Mangastream & MangaFox are supported")
        parser.add_argument("-au", "--add-user", help="Adds new user",
                            action="store_true")
        parser.add_argument("-lm", "--list-manga",
                            help="Lists Manga saved in database. If a Manga is passed, lists chapters to said Manga",
                            nargs="?", const='all')
        parser.add_argument("-lc", "--list-chapters", help="Lists the last 10 Chapters",
                            action="store_true")
        parser.add_argument("-Lc", "--list-chapters-all", help="Lists all Chapters",
                            action="store_true")
        parser.add_argument("-lf", "--list-feeds", help="Lists all feeds",
                            action="store_true")
        parser.add_argument("-lu", "--list-users", help="Lists all Users",
                            action="store_true")
        parser.add_argument("-cd", "--create-db", help="Creates DB. Uses Configfile for Naming",
                            action="store_true")
        parser.add_argument("-s", "--start", help="Starts one loop",
                            action="store_true")
        parser.add_argument("--send",
                            help="Sends Chapter directly by chapter ID. Multiple IDs can be given",
                            default=[], nargs='*',)
        parser.add_argument("--convert",
                            help="Converts Chapter directly by chapter ID. Multiple IDs can be given",
                            default=[], nargs='*',)
        parser.add_argument("--download",
                            help="Downloads Chapter directly by chapter ID. Multiple IDs can be given",
                            default=[], nargs='*',)
        parser.add_argument("-a", "--action",
                            help="Start action. Options are: rssparser (collecting feed data), downloader, converter or sender ")
        parser.add_argument("-ss", "--switch-send",
                            help="Pass ID of User. Switches said user Send eBook status")
        parser.add_argument("-dc", "--delete-chapter",
                            help="Pass ID of Chapter. Deletes said Chapter")
        parser.add_argument("-du", "--delete-user",
                            help="Pass ID of User. Deletes said User")
        parser.add_argument("-df", "--delete-feed",
                            help="Pass ID of Feed. Deletes said Feed")
        parser.add_argument("--daemon", help="Run as daemon",
                            action="store_true")
        parser.add_argument("-d", "--debug", help="Debug Mode",
                            action="store_true")
        parser.add_argument('-v', '--version',
                            action='version', version='%(prog)s ' + __version__)

        self.args = parser.parse_args()

        # Logging
        if self.args.debug:
            outputlevel = "debug"
        else:
            outputlevel = "info"
        helper.initialize_logger("log/", outputlevel)


        # Check if Arguments are passed or not. At least one is required
        if self.args.action is None \
            and self.args.add_feed is None \
            and self.args.delete_chapter is None \
            and self.args.delete_feed is None \
            and self.args.delete_user is None \
            and self.args.switch_send is None \
            and self.args.add_user is False \
            and self.args.list_manga is None \
            and not any([self.args.add_user,
                         self.args.create_db,
                         self.args.daemon,
                         self.args.list_chapters,
                         self.args.list_chapters_all,
                         self.args.list_feeds,
                         self.args.list_users,
                         self.args.download,
                         self.args.convert,
                         self.args.send,
                         self.args.start,]):
            logging.error("At least one argument is required!")

        logging.debug("Passed arguments: \n %s", self.args)


    def read_config(self):
        """ Reads the config """

        logging.debug("Loading configuration")
        config_reader = configparser.ConfigParser()
        config_reader.read("config.ini")
        self.config = config_reader["CONFIG"]

        logging.debug("Loaded Config:")
        logging.debug(self.config)



    '''
    Catch -af/--add-feed
    '''
    def save_feed_to_db(self):
        logging.debug("Entered URL: %s", self.args.add_feed)
        if validators.url(self.args.add_feed):
            helper.writeFeed(self.args.add_feed)
        else:
            logging.error("You need to enter an URL!")


    '''
    Catch -s/--switch-user
    '''
    def switch_user_status(self):
        logging.debug("Entered USERID: %s", self.args.switch_send)
        helper.switchUserSend(self.args.switch_send)


    '''
    Delete Stuff functions
    '''
    def delete_user(self):
        logging.debug("Entered USERID: %s", self.args.delete_user)
        helper.deleteUser(self.args.delete_user)

    def delete_chapter(self):
        logging.debug("Entered USERID: %s", self.args.delete_chapter)
        helper.deleteChapter(self.args.delete_chapter)

    def delete_feed(self):
        logging.debug("Entered USERID: %s", self.args.delete_feed)
        helper.deleteFeed(self.args.delete_feed)



    '''
    Catch --list-feeds
    '''
    def list_feeds(self):
        helper.printFeeds()


    '''
    Catch -L/--list-chapters-all
    '''
    def list_all_chapters(self):
        helper.printChaptersAll()


    '''
    Catch -l/--list-chapters
    '''
    def list_chapters(self):
        helper.printChapters()

    '''
    Catch -lm/--list-manga
    '''
    def list_manga(self):
        helper.printManga(self.args)



    '''
    Catch --list-users
    '''
    def list_users(self):
        helper.printUsers()

    '''
    Catch -u/--add-user
    '''
    def add_user(self):
        helper.createUser()

    '''
    Catch -cd/--create-db
    '''
    def create_db(self):
        helper.createDB()


    '''
    Catch -a / --action
    '''
    def start_action(self):

        # Start downloader
        if self.args.action == "downloader":
            logging.info("Starting downloader to get all outstanding/selected chapters")
            self.images_fetcher()
            logging.info("Finished downloading all chapters.")



        elif self.args.action == "rssparser":
            logging.info("Action '%s' is not yet implemented.", self.args.action)


        elif self.args.action == "converter":
            logging.info("Starting converter to convert all outstanding/selected chapters")
            self.image_converter()
            logging.info("Finished converting all chapters!")


        elif self.args.action == "sender":
            logging.info("Starting sender to send all outstanding/selected chapters")
            self.send_ebooks()
            logging.info("Finished sending all chapters!")

        else:
            logging.info("%s is not a valid action. Choose between  'rssparser', 'downloader', 'converter' or 'sender'", self.args.action)


    '''
    direct callers
    '''
    def send_chapter(self):
        msender.directSender(self.config, self.args.send)


    def convert_chapter(self):
        mconverter.directConverter(self.config, self.args.convert)


    def download_chapter(self):
        mdownloader.directDownloader(self.config, self.args.download)


    '''
    This are the worker, one round
    '''
    #  Worker to get and parse  rss feeds
    def parse_add_feeds(self):
        mparser.RssParser(self.config)

    # Worker to fetch all images
    def images_fetcher(self):
        mdownloader.downloader(self.config, self.args)

    # Worker to convert all downloaded chapters into ebooks
    def image_converter(self):
        mconverter.ConverterHandler(self.config, self.args)

    # Worker to convert all downloaded chapters into ebooks
    def send_ebooks(self):
        msender.SenderHandler(self.config, self.args)



    '''
    Application Run & Daemon loop
    '''
    def run(self):

        if self.args.add_feed:
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

        if self.args.list_manga:
            self.list_manga()
            return

        if self.args.add_user:
            self.add_user()
            return

        if self.args.list_users:
            self.list_users()
            return

        if self.args.delete_user:
            self.delete_user()
            return


        if self.args.delete_chapter:
            self.delete_chapter()
            return


        if self.args.delete_feed:
            self.delete_feed()
            return

        if self.args.create_db:
            self.create_db()
            return

        if self.args.action:
            self.start_action()
            return

        if self.args.send:
            self.send_chapter()
            return

        if self.args.download:
            self.download_chapter()
            return

        if self.args.convert:
            self.convert_chapter()
            return


        # Mainloop
        if self.args.start:
            daemon = True
            while daemon:
                if self.args.daemon:
                    logging.info("Don't forget that the daemon only handles data younger than 24h Hours!")
                else:
                    daemon = False

                logging.info("#########################")
                logging.info("Starting Loop at %s", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


                logging.info("Starting RSS Data Fetcher!")
                self.parse_add_feeds()
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

                if daemon:
                    logging.info("Sleeping for %s seconds...\n", (self.config["Sleep"]))
                    time.sleep(int(self.config["Sleep"]))

# Execute Main
if __name__ == '__main__':
    me = M2em()
    me.run()
