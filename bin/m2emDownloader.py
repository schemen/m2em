import logging
import os
import requests
from shutil import move
import bin.m2emHelper as helper
import bin.sourceparser.m2emMangastream as msparser
import bin.sourceparser.m2emMangafox as mxparser
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter


class Downloader:

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




    def data_collector(self, config, chapter):
        
        # Load configs required here
        self.database = config["Database"]
        self.saveloc  = config["SaveLocation"]

        # get relevant data of this Chapter
        self.mangastarturl   = chapter.url
        self.mangapages      = chapter.pages
        self.mangatitle      = chapter.title
        self.manganame       = chapter.manganame
        self.chapterdate     = chapter.date

        # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
        self.mangatitle = helper.sanetizeName(self.mangatitle)
        self.manganame = helper.sanetizeName(self.manganame)

        # Define Download location
        self.downloadfolder  = str(self.saveloc + self.manganame + "/" + self.mangatitle + "/images")

        # get Origin of manga (Which mangawebsite)
        self.origin = helper.getSourceURL(self.mangastarturl)
        
        # Initiate URL list
        self.imageurls=[]




    def data_processor(self):

        logging.info("Proccesing data for %s"% self.mangatitle)


        # Get image urls!
        # Mangastream Parser
        if self.origin == "mangastream.com" or self.origin == "readms.net":
            urllist = msparser.getPagesUrl(self.mangastarturl,self.mangapages)


            # Turn Manga pages into Image links!
            for i in urllist:
                self.imageurls.append(msparser.getImageUrl(i))
            logging.debug("List of all Images for %s" % self.mangatitle)
            logging.debug(self.imageurls)


        # Mangafox Parser
        elif self.origin == "mangafox.me" or self.origin == "mangafox.la":
            urllist = mxparser.getPagesUrl(self.mangastarturl,self.mangapages)


            # Turn Manga pages into Image links!
            for i in urllist:
                self.imageurls.append(mxparser.getImageUrl(i))
            logging.debug("List of all Images for %s" % self.mangatitle)
            logging.debug(self.imageurls)





    def downloader(self):
        logging.info("Starting download of %s..." % self.mangatitle)
        # Download & save images!
        # check if we have images to download
        if not len(self.imageurls) == 0:

            # Check if we have the Download folder
            helper.createFolder(self.downloadfolder)

            # Start download Task
            counter = 0
            for image in self.imageurls:
                counter = counter + 1

                imagepath = self.downloadfolder + "/" + str("{0:0=3d}".format(counter)) + ".png"
                tempdl = self.downloadfolder + "/" + str("{0:0=3d}".format(counter)) + ".tmp"

                # Download the image!
                f = open(tempdl, 'wb')
                f.write(requests.get(image).content)
                f.close()

                # If everything is alright, write image to final name
                os.rename(tempdl, imagepath)


                # Cleanse image, remove footer
                #
                #   I have borrowed this code from the kmanga project.
                #   https://github.com/aplanas/kmanga/blob/master/mobi/mobi.py#L416
                #   Thanks a lot to Alberto Planas for coming up with it!
                #
                if self.origin == "mangafox.me" or self.origin == "mangafox.la":
                    logging.debug("Cleaning Mangafox Footer")
                    img = Image.open(imagepath)
                    _img = ImageOps.invert(img.convert(mode='L'))
                    _img = _img.point(lambda x: x and 255)
                    _img = _img.filter(ImageFilter.MinFilter(size=3))
                    _img = _img.filter(ImageFilter.GaussianBlur(radius=5))
                    _img = _img.point(lambda x: (x >= 48) and x)

                    cleaned = img.crop(_img.getbbox()) if _img.getbbox() else img
                    cleaned.save(imagepath)

            # Finish :)
            logging.info("Finished download of %s!"% self.mangatitle)