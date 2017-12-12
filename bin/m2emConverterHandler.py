import logging
import os
import bin.m2emHelper as helper
from bin.m2emConverter import Converter


def ConverterHandler(config, args):
    """ Function that handles the Converter in a loop """

    # Load configs required here
    database = config["Database"]

    # Load Chapters!
    chapters = helper.getChapters(database)


    # Start conversion loop!
    for chapter in chapters:



        # Verify if chapter has been downloaded already
        if not helper.verifyDownload(config, chapter):
            logging.debug("Manga %s has not been downloaded!", chapter[2])
        else:


            # Spawn an Converter Object & get basic data from database & config
            current_conversation = Converter()
            current_conversation.data_collector(config, chapter)

            # Check if Download loop & Download task is selected
            if not args.start:
                current_conversation.cbz_creator()
                current_conversation.eb_creator()
            else:

                # Only start run if chapter is younger than 24h
                if helper.checkTime(current_conversation.chapterdate):
                    current_conversation.cbz_creator()
                    current_conversation.eb_creator()
                else:
                    logging.debug("%s is older than 24h, will not be processed by daemon.",
                                  current_conversation.mangatitle)




def directConverter(config, chapterids=[]):
    """ Function that handles direct calls of the Converter """

    logging.debug("Following Chapters are directly converted:")
    logging.debug(chapterids)

    # Load configs required here
    database = config["Database"]


    chapters = helper.getChaptersFromID(database, chapterids)


    if not chapters:
        logging.error("No Chapters found with said ID!")
    else:
        # Start conversion loop!
        for chapter in chapters:

            # Verify if chapter has been downloaded already
            if not helper.verifyDownload(config, chapter):
                logging.info("Manga %s has not been downloaded!", chapter[2])
            else:


                # Spawn an Converter Object & get basic data from database & config
                current_conversation = Converter()
                current_conversation.data_collector(config, chapter)

                if os.path.exists(current_conversation.cbzlocation):
                    logging.info("Manga %s converted to CBZ already!",
                                 current_conversation.mangatitle)
                else:
                    logging.info("Starting conversion to CBZ of %s...",
                                 current_conversation.mangatitle)
                    current_conversation.cbz_creator()

                # Start conversion to Ebook format!
                if os.path.exists(current_conversation.eblocation):
                    logging.info("Manga %s converted to Ebook already!",
                                 current_conversation.mangatitle)
                else:
                    logging.info("Starting conversion to Ebook of %s...",
                                 current_conversation.mangatitle)
                    current_conversation.eb_creator()
