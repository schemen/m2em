import logging
import os
import bin.m2emHelper as helper
from bin.m2emSender import Sender

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def SenderHandler(config, args):
    """ Function that handles the sending of ebooks when a loop is called """


    # Load configs required here
    database = config["Database"]

    # Get all Chapters
    chapters = helper.getChapters(database)

    # Load Users
    users = helper.getUsers(database)

    # Debug Users:
    logging.debug("Userlist:")
    logging.debug(users)



    # Start conversion loop!
    for chapter in chapters:

        # Initiate Sender class and fill it with data
        current_sender = Sender()
        current_sender.data_collector(config, chapter)
        current_sender.database = database
        current_sender.users = users

        # Check if ebook has been converted yet, else skip
        if not os.path.exists(current_sender.eblocation):
            logging.debug("Manga %s has not been converted yet.", current_sender.mangatitle)
        else:

            # Check if Chapter has been sent already
            if current_sender.issent != 0:
                logging.debug("%s has been sent already!", current_sender.mangatitle)
            else:

                # Check if Sender loop or Sender task is selected
                if not args.start:
                    logging.info("Sending %s...", current_sender.mangatitle)
                    current_sender.send_eb()
                else:

                    # Only start run if chapter is younger than 24h
                    if helper.checkTime(current_sender.chapterdate):
                        logging.info("Sending %s...", current_sender.mangatitle)
                        current_sender.send_eb()
                    else:
                        logging.debug("%s is older than 24h, will not be processed by daemon.",
                                      current_sender.mangatitle)


def directSender(config, chapterids=[]):
    """ Function that handles the coordination of directly sending ebooks """

    logging.debug("Following Chapters are directly sent:")
    logging.debug(chapterids)

    # Load configs required here
    database = config["Database"]


    chapters = helper.getChaptersFromID(database, chapterids)

    # Load Users
    users = helper.getUsers(database)

    # Debug Users:
    logging.debug("Userlist:")
    logging.debug(users)


    if not chapters:
        logging.error("No Chapters found with said ID!")
    else:
        # Start conversion loop!
        for chapter in chapters:

            # Initiate Sender class and fill it with data
            current_sender = Sender()
            current_sender.data_collector(config, chapter)
            current_sender.database = database
            current_sender.users = users

            # Check if ebook has been converted yet, else skip
            if not os.path.exists(current_sender.eblocation):
                logging.debug("Manga %s has not been converted yet.", current_sender.mangatitle)
            else:
                logging.info("Sending %s...", current_sender.mangatitle)
                current_sender.send_eb()
