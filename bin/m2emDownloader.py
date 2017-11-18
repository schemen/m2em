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

def ChapterDownloader(config):
    
    # Load configs required here
    database = config["Database"]
    saveloc  = config["SaveLocation"]

    # Load Chapters from Database
    chapters = helper.getChapters(database)
    logging.debug("Loaded Chapers:")
    for i in chapters:
        logging.debug(i)


    # Start Download loop!
    for chapter in chapters:

        # get relevant data of this Manga
        mangastarturl   = chapter[4]
        mangapages      = chapter[9]
        mangatitle      = chapter[2]
        manganame       = chapter[11]

        # check if mangatitle contains ":" characters that OS can't handle as folders
        mangatitle = helper.sanetizeName(mangatitle)

        # check if manganame contains ":" characters that OS can't handle as folders
        manganame = helper.sanetizeName(manganame)

        # Old Download folder from v0.1.0
        oldlocation = str(saveloc + mangatitle)
        newlocation = str(saveloc + manganame)

        # Define Download location
        downloadfolder  = str(saveloc + manganame + "/" + mangatitle + "/images")


        # Check if the old DL location is being used
        if os.path.isdir(oldlocation):
            logging.info("Moving old DL location to new one")
            helper.createFolder(newlocation)
            move(oldlocation, newlocation)


        if os.path.isdir(downloadfolder):
            logging.debug("Manga %s downloaded already!" % mangatitle)
        else:
            logging.info("Starting download of %s..." % mangatitle)


            # get Origin of manga
            origin = helper.getSourceURL(mangastarturl)


            # Get image urls!
            if origin == "mangastream.com":
                urllist = msparser.getPagesUrl(mangastarturl,mangapages)


                # Turn Manga pages into Image links!
                imageurls=[]
                for i in urllist:
                    imageurls.append(msparser.getImageUrl(i))
                logging.debug("List of all Images for %s" % mangatitle)
                logging.debug(imageurls)
                

            # Mangafox Parser
            elif origin == "mangafox.me":
                urllist = mxparser.getPagesUrl(mangastarturl,mangapages)


                # Turn Manga pages into Image links!
                imageurls=[]
                for i in urllist:
                    imageurls.append(mxparser.getImageUrl(i))
                logging.debug("List of all Images for %s" % mangatitle)
                logging.debug(imageurls)

            else:
                pass


            # Download & save images!
            # check if we have images to download
            if not len(imageurls) == 0:
                helper.createFolder(downloadfolder)
                counter = 0
                for image in imageurls:
                    counter = counter + 1

                    imagepath = downloadfolder + "/" + str("{0:0=3d}".format(counter)) + ".png"

                    f = open(imagepath, 'wb')
                    f.write(requests.get(image).content)
                    f.close


                    # Cleanse image, remove footer
                    #
                    #   I have borrowed this code from the kmanga project.
                    #   https://github.com/aplanas/kmanga/blob/master/mobi/mobi.py#L416
                    #   Thanks a lot to Alberto Planas for coming up with it!
                    #
                    if origin == "mangafox.me":
                        logging.debug("Cleaning Mangafox")
                        img = Image.open(imagepath)
                        _img = ImageOps.invert(img.convert(mode='L'))
                        _img = _img.point(lambda x: x and 255)
                        _img = _img.filter(ImageFilter.MinFilter(size=3))
                        _img = _img.filter(ImageFilter.GaussianBlur(radius=5))
                        _img = _img.point(lambda x: (x >= 48) and x)

                        cleaned = img.crop(_img.getbbox()) if _img.getbbox() else img
                        cleaned.save(imagepath)



                logging.info("Finished download!")