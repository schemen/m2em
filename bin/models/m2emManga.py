import sqlite3
import logging
import bin.m2emHelper as helper


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


    #def __repr__(self):
    #    return '<Manga: %s - %s>' % (self.manga_name, self.chapter)

    def load_from_feed(self, entry, parent_feed):
        self.chapter_link = entry.link

        # Getting specific manga data
        logging.debug("Fetching Data from Weblink")
        mangadata = helper.getMangaData(self.chapter_link)
        logging.debug("Finished Collecting Chapter Data!")

        self.manga_name = mangadata[0]
        self.title = entry.title
        self.chapter = mangadata[2]
        self.chapter_name = entry.description
        self.chapter_pages = mangadata[1]
        self.chapter_pubDate = entry.published
        self.parent_feed = parent_feed

    def print_manga(self):
        logging.info("Title:         {}".format(self.title))
        logging.info("Manga:         {}".format(self.manga_name))
        logging.info("Chapter:       {}".format(self.chapter))
        logging.info("Chapter Name:  {}".format(self.chapter_name))
        logging.info("Chapter Pages: {}".format(self.chapter_pages))
        logging.info("Released on:   {}".format(self.chapter_pubDate))
        logging.info("URL:           {}".format(self.chapter_link))
        logging.info("Parent feed:   {}".format(self.parent_feed))


    def save(self):
        if not self.database:
            logging.error("No database specified")
            return False

        # Open Database
        try:
            conn = sqlite3.connect(self.database)
        except Exception as e:
            logging.error("Could not connect to DB %s" % e)
            return False
        logging.debug("Succesfully Connected to DB %s" % self.database)
        c = conn.cursor()
        logging.info("Checking if chapter is already saved...")

        # Check if Feed is already saved in DB
        c.execute("SELECT url FROM chapter WHERE url = ?", (str(self.chapter_link),))
        duplicated = c.fetchall()


        logging.debug("Duplicated Data: %s" % duplicated)
        if len(duplicated) != 0:
            logging.info("Manga is already in Database! Skipping...")
        else:
            logging.info("Saving Chapter Data...")
            c.execute("insert into chapter (origin, title, date, url, desc, ispulled, isconverted, issent, pages, chapter, manganame) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (self.parent_feed,
                      self.title,
                      self.chapter_pubDate,
                      self.chapter_link,
                      self.chapter_name,
                      self.ispulled,
                      self.isconverted,
                      self.issent,
                      self.chapter_pages,
                      self.chapter,
                      self.manga_name))
            conn.commit()
            logging.info("Succesfully saved Data!")

        conn.close()
        logging.info("\n")
