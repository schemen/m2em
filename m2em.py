#!/usr/bin/env python
""" Main Wrapper Module """
import os
import sys
import logging
import time
import argparse
import datetime
import validators
from bin._version import __version__
# Start of the fun!
import bin.Config as Config
import bin.Helper as helper
import bin.RssParser as mparser
import bin.DownloaderHandler as mdownloader
import bin.ConverterHandler as mconverter
import bin.SenderHandler as msender
import bin.Migrator as migrator

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
            self.config = Config.load_config()
            logging.debug("Loaded Config:")
            logging.debug(self.config)

        # Check if Database exists, else create
        if not os.path.isfile(self.config["Database"]):
            helper.createFolder(self.config["SaveLocation"])
            helper.createDB()

        # Check weather there are some database migrations
        mversion = helper.getMigrationVersion() + ".py"
        if self.config["DisableMigrations"] == "True":
            logging.debug("Migrations disabled! Current version: %s ", mversion)
        else:
            if mversion in os.listdir(os.getcwd() + "/migrations"):
                logging.debug("No migrations required! Current version: %s ", mversion)
            else:
                migrator.migrate()


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
        parser.add_argument("-p", "--process",
                            help="Processes chapter(s) by chapter ID, Download, convert, send. Multiple IDs can be given",
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
        parser.add_argument('-f', '--filter',
                            help='Adds a filter(python regex format), to filter the title of any manga parsed. Example: "(?i)one-punch"',
                            nargs=1, metavar='"filter_regex"')
        parser.add_argument('-fl', '--filter-list',
                            help='Lists all filters',
                            action='store_true')

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
            and self.args.filter is None \
            and self.args.filter_list is None \
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
                         self.args.process,
                         self.args.start,]):
            logging.error("At least one argument is required!")

        logging.debug("Passed arguments: \n %s", self.args)


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
    Catch -f/--filter
    '''
    def add_filter(self):
        if len(self.args.filter) > 0:
            filter_value = self.args.filter[0]
            logging.debug("Entered filter: %s", filter_value)
            helper.writeFilter(filter_value)
        else:
            logging.error("You need to enter a filter value!")

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
    Catch -lf/--list-feeds
    '''
    def list_feeds(self):
        helper.printFeeds()

    '''
    Catch -fl/--filter-list
    '''
    def filter_list(self):
        helper.printFilters()
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
        msender.directSender(self.args.send)


    def convert_chapter(self):
        mconverter.directConverter(self.args.convert)


    def download_chapter(self):
        mdownloader.directDownloader(self.args.download)


    def process_chapter(self):
        mdownloader.directDownloader(self.args.process)
        mconverter.directConverter(self.args.process)
        msender.directSender(self.args.process)

    '''
    This are the worker, one round
    '''
    #  Worker to get and parse  rss feeds
    def parse_add_feeds(self):
        mparser.RssParser()

    # Worker to fetch all images
    def images_fetcher(self):
        mdownloader.downloader(self.args)

    # Worker to convert all downloaded chapters into ebooks
    def image_converter(self):
        mconverter.ConverterHandler(self.args)

    # Worker to convert all downloaded chapters into ebooks
    def send_ebooks(self):
        msender.SenderHandler(self.args)



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

        if self.args.process:
            self.process_chapter()
            return

        if self.args.filter:
            self.add_filter()
            return

        if self.args.filter_list:
            self.filter_list()
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
