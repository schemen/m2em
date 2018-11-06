"""Downloader Module"""
import logging
import os
import requests
import bin.Config as Config
import bin.Helper as helper
import bin.sourceparser.Mangastream as msparser
import bin.sourceparser.Mangafox as mxparser
import bin.sourceparser.Cdmnet as cdmparser
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter


class Downloader:
    """Class to manage downloads"""

    def __init__(self):
        self.database = None
        self.saveloc = None
        self.mangastarturl = None
        self.mangapages = None
        self.mangatitle = None
        self.manganame = None
        self.chapterdate = None
        self.downloadfolder = None
        self.origin = None
        self.imageurls = None




    def data_collector(self, chapter):
        """Method to collect and fill data for the class"""

        # Load config right at the start
        config = None
        if not config:
            config = Config.load_config()

        # Load configs required here
        self.database = config["Database"]
        self.saveloc = config["SaveLocation"]

        # get relevant data of this Chapter
        self.mangastarturl = chapter.url
        self.mangapages = chapter.pages
        self.mangatitle = chapter.title
        self.manganame = chapter.manganame
        self.chapterdate = chapter.date

        # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
        self.mangatitle = helper.sanetizeName(self.mangatitle)
        self.manganame = helper.sanetizeName(self.manganame)

        # Define Download location
        self.downloadfolder = str(self.saveloc + self.manganame + "/" + self.mangatitle + "/images")

        # get Origin of manga (Which mangawebsite)
        self.origin = helper.getSourceURL(self.mangastarturl)

        # Initiate URL list
        self.imageurls = []




    def data_processor(self):
        """Method that starts processing the collected data"""

        logging.info("Proccesing data for %s", self.mangatitle)


        # Get image urls!
        # Mangastream Parser
        if self.origin == "mangastream.com" or self.origin == "readms.net":
            urllist = msparser.getPagesUrl(self.mangastarturl, self.mangapages)

            # check if we have images to download
            if not len(urllist) == 0:

                # Turn Manga pages into Image links!
                logging.info("Starting download of %s...", self.mangatitle)
                counter = 0
                for i in urllist:
                    counter = counter + 1
                    self.downloader(i, counter, msparser.getImageUrl)


            # Finish :)
            logging.info("Finished download of %s!", self.mangatitle)

        # Mangafox Parser
        elif self.origin == "mangafox.me" or self.origin == "mangafox.la" or self.origin == "fanfox.net":
            urllist = mxparser.getPagesUrl(self.mangastarturl, self.mangapages)

            # check if we have images to download
            if not len(urllist) == 0:

                # Turn Manga pages into Image links!
                logging.info("Starting download of %s...", self.mangatitle)
                counter = 0
                for i in urllist:
                    counter = counter + 1
                    self.downloader(i, counter, mxparser.getImageUrl)


            # Finish :)
            logging.info("Finished download of %s!", self.mangatitle)

        # CDM Parser
        elif self.origin == "cdmnet.com.br":
            urllist = cdmparser.getPagesUrl(self.mangastarturl, self.mangapages)

            # check if we have images to download
            if not len(urllist) == 0:

                # Turn Manga pages into Image links!
                logging.info("Starting download of %s...", self.mangatitle)
                counter = 0
                for i in urllist:
                    counter = counter + 1
                    self.downloader(i, counter, cdmparser.getImageUrl)


            # Finish :)
            logging.info("Finished download of %s!", self.mangatitle)

    def downloader(self, url, counter, parser):
        """Method that downloads files"""

        # Check if we have the Download folder
        helper.createFolder(self.downloadfolder)

        imagepath = self.downloadfolder + "/" + str("{0:0=3d}".format(counter)) + ".png"
        tempdl = self.downloadfolder + "/" + str("{0:0=3d}".format(counter)) + ".tmp"

        # Download the image!
        f = open(tempdl, 'wb')
        f.write(requests.get(parser(url), headers={'referer': url}).content)
        f.close()

        # convert img to png
        imgtest = Image.open(tempdl)
        if imgtest.format != 'PNG':
            logging.debug("Image %s is not a PNG... convertig.", tempdl)
            imgtest.save(tempdl, "PNG")
        else:
            imgtest.close()

        # If everything is alright, write image to final name
        os.rename(tempdl, imagepath)


        # Cleanse image, remove footer
        #
        #   I have borrowed this code from the kmanga project.
        #   https://github.com/aplanas/kmanga/blob/master/mobi/mobi.py#L416
        #   Thanks a lot to Alberto Planas for coming up with it!
        #
        if self.origin == "mangafox.me" or self.origin == "mangafox.la" or self.origin == "fanfox.net":
            logging.debug("Cleaning Mangafox Footer")
            img = Image.open(imagepath)
            _img = ImageOps.invert(img.convert(mode='L'))
            _img = _img.point(lambda x: x and 255)
            _img = _img.filter(ImageFilter.MinFilter(size=3))
            _img = _img.filter(ImageFilter.GaussianBlur(radius=5))
            _img = _img.point(lambda x: (x >= 48) and x)

            cleaned = img.crop(_img.getbbox()) if _img.getbbox() else img
            cleaned.save(imagepath)
