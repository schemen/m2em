import logging
import os
from shutil import move
import bin.m2emHelper as helper
from bin.m2emDownloader import Downloader
import threading
import queue

'''
downloadHandler
'''
class DownloadHandler():

    def __init__(self, config, args):
        self.config = config
        self.args = args


    def downloader(self):

        # Load configs required here
        database = self.config["Database"]


        chapters = helper.getChapters(database)

        if self.args.start:
            logging.debug("The loop will only consider Chapters younger than 24h!")

        q = queue.Queue()
        num_threads = 5


        for chapter in chapters:
            q.put(chapter)

        for i in range(num_threads):
            worker = threading.Thread(target=self.dlprocessor, args=(q,))
            worker.setDaemon(True)
            worker.start()

        q.join()
            # Start Download loop!
        #for chapter in chapters:


            # # Initialize Downloader class & load basic params
            # current_chapter = Downloader()
            # current_chapter.data_collector(config,chapter)
            #
            #
            # # Check if the old DL location is being used and fix it!
            # oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
            # newlocation = str(current_chapter.saveloc + current_chapter.manganame)
            # if os.path.isdir(oldlocation):
            #     logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
            #     helper.createFolder(newlocation)
            #     move(oldlocation, newlocation)
            #
            #
            #
            # # Check if chapter needs to be downloaded
            # if helper.verifyDownload(config, chapter):
            #     logging.debug("Manga %s downloaded already!" % current_chapter.mangatitle)
            # else:
            #
            #     # Check if Download loop & Download task is selected
            #     if not args.start:
            #         current_chapter.data_processor()
            #         current_chapter.downloader()
            #     else:
            #
            #         # Only start run if chapter is younger than 24h
            #         if  helper.checkTime(current_chapter.chapterdate):
            #             current_chapter.data_processor()
            #             current_chapter.downloader()
            #         else:
            #             logging.debug("%s is older than 24h, will not be processed by daemon." % current_chapter.mangatitle)



    def dlprocessor(self,q):

        while threading.main_thread().isAlive:
            chapter = q.get()
            # Initialize Downloader class & load basic params
            current_chapter = Downloader()
            current_chapter.data_collector(self.config, chapter)

            # Check if the old DL location is being used and fix it!
            oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
            newlocation = str(current_chapter.saveloc + current_chapter.manganame)
            if os.path.isdir(oldlocation):
                logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
                helper.createFolder(newlocation)
                move(oldlocation, newlocation)

            # Check if chapter needs to be downloaded
            if helper.verifyDownload(self.config, chapter):
                logging.debug("Manga %s downloaded already!" % current_chapter.mangatitle)
            else:

                # Check if Download loop & Download task is selected
                if not self.args.start:
                    current_chapter.data_processor()
                    current_chapter.downloader()
                else:

                    # Only start run if chapter is younger than 24h
                    if helper.checkTime(current_chapter.chapterdate):
                        current_chapter.data_processor()
                        current_chapter.downloader()
                    else:
                        logging.debug("%s is older than 24h, will not be processed by daemon." % current_chapter.mangatitle)
            q.task_done()



    def directdlprocessor(self,chapter):

        # Initialize Downloader class & load basic params
        current_chapter = Downloader()
        current_chapter.data_collector(self.config, chapter)

        # Check if the old DL location is being used and fix it!
        oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
        newlocation = str(current_chapter.saveloc + current_chapter.manganame)
        if os.path.isdir(oldlocation):
            logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
            helper.createFolder(newlocation)
            move(oldlocation, newlocation)

        # Check if chapter needs to be downloaded
        if helper.verifyDownload(self.config, chapter):
            logging.info("Manga %s downloaded already!" % current_chapter.mangatitle)
        else:

            current_chapter.data_processor()
            current_chapter.downloader()


    def directDownloader(self, chapterids=[]):

        logging.debug("Following Chapters are directly converted:")
        logging.debug(chapterids)

        # Load configs required here
        database    = self.config["Database"]


        chapters = helper.getChaptersFromID(database, chapterids)

        # Load Users
        users    = helper.getUsers(database)

        # Debug Users:
        logging.debug("Userlist:")
        logging.debug(users)


        if not chapters:
            logging.error("No Chapters found with said ID!")
        else:
            pool = multiprocessing.Pool(5)

            for chapter in chapters:
                pool.Process(self.directdlprocessor(chapter))

            pool.close()
            # # Start conversion loop!
            # for chapter in chapters:
            #
            #     # Initialize Downloader class & load basic params
            #     current_chapter = Downloader()
            #     current_chapter.data_collector(config, chapter)
            #
            #     # Check if the old DL location is being used and fix it!
            #     oldlocation = str(current_chapter.saveloc + current_chapter.mangatitle)
            #     newlocation = str(current_chapter.saveloc + current_chapter.manganame)
            #     if os.path.isdir(oldlocation):
            #         logging.info("Moving %s from old DL location to new one..." % current_chapter.mangatitle)
            #         helper.createFolder(newlocation)
            #         move(oldlocation, newlocation)
            #
            #     # Check if chapter needs to be downloaded
            #     if helper.verifyDownload(config, chapter):
            #         logging.info("Manga %s downloaded already!" % current_chapter.mangatitle)
            #     else:
            #
            #         current_chapter.data_processor()
            #         current_chapter.downloader()
