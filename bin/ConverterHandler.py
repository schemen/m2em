""" Module that handles the workflow of the Converter Class """
import logging
import os
import bin.Helper as helper
from bin.Converter import Converter

def ConverterHandler(args):
    """ Function that handles the Converter in a loop """

    # Load Chapters!
    chapters = helper.getChapters()


    # Start conversion loop!
    for chapter in chapters.iterator():


        # Verify if chapter has been downloaded already
        if not helper.verifyDownload(chapter):
            logging.debug("Manga %s has not been downloaded!", chapter.title)
        else:


            # Spawn an Converter Object & get basic data from database & config
            current_conversation = Converter()
            current_conversation.data_collector(chapter)

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




def directConverter(chapterids=[]):
    """ Function that handles direct calls of the Converter """

    logging.debug("Following Chapters are directly converted:")
    logging.debug(chapterids)

    chapters = helper.getChaptersFromID(chapterids)


    if not chapters:
        logging.error("No Chapters found with said ID!")
    else:
        # Start conversion loop!
        for chapter in chapters:

            # Verify if chapter has been downloaded already
            if not helper.verifyDownload(chapter):
                logging.info("Manga %s has not been downloaded!", chapter[2])
            else:


                # Spawn an Converter Object & get basic data from database & config
                current_conversation = Converter()
                current_conversation.data_collector(chapter)

                if os.path.exists(current_conversation.cbzlocation):
                    logging.info("Manga %s converted to CBZ already!",
                                 current_conversation.mangatitle)
                else:
                    current_conversation.cbz_creator()

                # Start conversion to Ebook format!
                if os.path.exists(current_conversation.eblocation):
                    logging.info("Manga %s converted to Ebook already!",
                                 current_conversation.mangatitle)
                else:
                    current_conversation.eb_creator()
