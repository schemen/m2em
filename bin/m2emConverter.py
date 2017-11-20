import logging
import os
import zipfile
import subprocess
import bin.m2emHelper as helper


def RecursiveConverter(config):

    # Load configs required here
    database  = config["Database"]
    saveloc   = config["SaveLocation"]
    ebformat  = config["EbookFormat"]
    ebprofile = config["EbookProfile"]

    # Load Chapters from Database
    chapters = helper.getChapters(database)


    # Start conversion loop!
    for chapter in chapters:

        # get relevant data of this Manga
        mangatitle   = chapter[2]
        manganame    = chapter[11]

        # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
        mangatitle = helper.sanetizeName(mangatitle)
        manganame = helper.sanetizeName(manganame)


        # create folder variables
        imagefolder  = str(saveloc + manganame + "/"+  mangatitle + "/images/")
        eblocation   = str(saveloc + manganame + "/"+  mangatitle + "/" + mangatitle + "." + ebformat.lower())
        cbzlocation  = str(saveloc + manganame + "/"+ mangatitle + "/" + mangatitle + ".cbz")

        # Verify if chapter has been downloaded already
        if not helper.verifyDownload(config, chapter):
            logging.debug("Manga %s has not been downloaded!" % mangatitle)
        else:

            # Create CBZ to make creation easier
            if os.path.exists(cbzlocation):
                logging.debug("Manga %s converted to CBZ already!" % mangatitle)
            else:
                logging.info("Starting conversion to CBZ of %s..." % mangatitle)


                logging.debug("Opening CBZ archive...")
                try:
                    zf = zipfile.ZipFile(cbzlocation, "w")
                except Exception as e:
                    logging.warning("Failed opening archive! %s" % e)



                logging.debug("Writing Images into CBZ")
                for img in sorted(os.listdir(imagefolder)):
                    image = imagefolder + img
                    logging.debug("Writing %s" % image)
                    zf.write(image,img)

                zf.close()


            # Start conversion to Ebook format!
            if os.path.exists(eblocation):
                logging.debug("Manga %s converted to Ebook already!" % mangatitle)
            else:
                logging.info("Starting conversion to Ebook of %s..." % mangatitle)

                try:
                    subprocess.call(["kcc-c2e", "-p", ebprofile, "-f", ebformat, "-m", "-q", "-r",  "2", "-u", "-s",  cbzlocation])
                except Exception as e:
                    logging.debug("Failed to convert epub %s" % e)

def ChapterConverter(imagelocation, config):
    pass