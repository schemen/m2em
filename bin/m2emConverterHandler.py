import logging
import bin.m2emHelper as helper
from bin.m2emConverter import Converter


def ConverterHandler(config, args, chapterids=[]):

    # Load configs required here
    database  = config["Database"]

    if not chapterids:
        # Load Chapters from Database
        chapters = helper.getChapters(database)
    else:
        # TODO Create helper function to extract chapters out of chapter IDs
        pass


    # Start conversion loop!
    for chapter in chapters:



        # Verify if chapter has been downloaded already
        if not helper.verifyDownload(config, chapter):
            logging.debug("Manga %s has not been downloaded!" % chapter[2])
        else:


            # Spawn an Converter Object & get basic data from database & config
            current_conversation = Converter()
            current_conversation.data_collector(config,chapter)

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
                    logging.debug("%s is older than 24h, will not be processed by daemon." % current_conversation.mangatitle)

