import logging
from bin.Models import *
import bin.Helper as helper


class Manga:

    def __init__(self):
        self.title = None
        self.manga_name = None
        self.chapter = None
        self.chapter_name = None
        self.chapter_pages = None
        self.chapter_pubDate = None
        self.chapter_link = None
        self.parent_feed = None
        self.database = None
        self.ispulled = None
        self.isconverted = None
        self.issent = None
        self.duplicated = None


    def load_from_feed(self, entry, parent_feed):
        self.chapter_link = entry.link

        # Check if link is already in DB to make sure only data gets downloaded that is not yet downloaded
        logging.debug("Checking if chapter is already saved...")
        db.get_conn()
        self.duplicated = Chapter.select().where(Chapter.url==self.chapter_link)

        if self.duplicated.exists():
            logging.debug("Manga is already in Database! Skipping...")
        else:

            # Getting specific manga data
            logging.debug("Fetching Data from Weblink")
            mangadata = helper.getMangaData(self.chapter_link, entry)
            logging.debug("Finished Collecting Chapter Data!")

            self.manga_name = mangadata[0]
            self.title = mangadata[3]
            self.chapter = mangadata[2]
            self.chapter_name = mangadata[4]
            self.chapter_pages = mangadata[1]
            self.chapter_pubDate = mangadata[5]
            self.parent_feed = parent_feed

            # Set some defaul values
            self.ispulled = 0
            self.isconverted = 0
            self.issent = 0

    def print_manga(self):
        logging.debug("Title:         {}".format(self.title))
        logging.debug("Manga:         {}".format(self.manga_name))
        logging.debug("Chapter:       {}".format(self.chapter))
        logging.debug("Chapter Name:  {}".format(self.chapter_name))
        logging.debug("Chapter Pages: {}".format(self.chapter_pages))
        logging.debug("Released on:   {}".format(self.chapter_pubDate))
        logging.debug("URL:           {}".format(self.chapter_link))
        logging.debug("Parent feed:   {}".format(self.parent_feed))


    def save(self):

        if self.duplicated.exists():
            logging.debug("Manga is already in Database! Skipping...")
        else:
            logging.info("Saving Chapter Data for %s", self.title)
            db.get_conn()
            chapter = Chapter()
            chapter.chapter = self.chapter
            chapter.date = self.chapter_pubDate
            chapter.desc = self.chapter_name
            chapter.isconverted = self.isconverted
            chapter.ispulled = self.ispulled
            chapter.issent = self.issent
            chapter.manganame = self.manga_name
            chapter.origin = self.parent_feed
            chapter.pages = self.chapter_pages
            chapter.title = self.title
            chapter.url = self.chapter_link
            chapter.save()
            logging.info("Succesfully saved Data!")

        logging.debug("\n")
