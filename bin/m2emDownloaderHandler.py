import logging
import os
from shutil import move
import bin.m2emHelper as helper
from bin.m2emDownloader import Downloader


'''
downloadHandler
'''
def downloader(config, args):
    
    # Load configs required here
    database = config["Database"]


    chapters = helper.getChapters(database)

    if args.start:
        logging.debug("The loop will only consider Chapters younger than 24h!")



    # Start Download loop!
    for chapter in chapters:

        # Initialize Downloader class & load basic params
        current_chapter = Downloader()
        current_chapter.data_collector(config,chapter)


        # Check if the old DL location is being used and fix it!
        oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
        newlocation = str(current_chapter.saveloc + current_chapter.manganame)
        if os.path.isdir(oldlocation):
            logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
            helper.createFolder(newlocation)
            move(oldlocation, newlocation)



        # Check if chapter needs to be downloaded
        if helper.verifyDownload(config, chapter):
            logging.debug("Manga %s downloaded already!" % current_chapter.mangatitle)
        else:

            # Check if Download loop & Download task is selected
            if not args.start:
                current_chapter.data_processor()
                current_chapter.downloader()
            else:

                # Only start run if chapter is younger than 24h
                if  helper.checkTime(current_chapter.chapterdate):
                    current_chapter.data_processor()
                    current_chapter.downloader()
                else:
                    logging.debug("%s is older than 24h, will not be processed by daemon." % current_chapter.mangatitle)


def directDownloader(config, chapterids=[]):

    logging.debug("Following Chapters are directly converted:")
    logging.debug(chapterids)

    # Load configs required here
    database    = config["Database"]


    chapters = helper.getChaptersFromID(database, chapterids)

    # Load Users
    users    = helper.getUsers(database)

    # Debug Users:
    logging.debug("Userlist:")
    logging.debug(users)


    if not chapters:
        logging.error("No Chapters found with said ID!")
    else:
        # Start conversion loop!
        for chapter in chapters:

            # Initialize Downloader class & load basic params
            current_chapter = Downloader()
            current_chapter.data_collector(config, chapter)

            # Check if the old DL location is being used and fix it!
            oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
            newlocation = str(current_chapter.saveloc + current_chapter.manganame)
            if os.path.isdir(oldlocation):
                logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
                helper.createFolder(newlocation)
                move(oldlocation, newlocation)

            # Check if chapter needs to be downloaded
            if helper.verifyDownload(config, chapter):
                logging.info("Manga %s downloaded already!" % current_chapter.mangatitle)
            else:

                current_chapter.data_processor()
                current_chapter.downloader()
