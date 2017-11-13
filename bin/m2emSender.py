import logging
import os
import bin.m2emHelper as helper
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders

def sendEbook(config):
    # Load configs required here
    database    = config["Database"]
    saveloc     = config["SaveLocation"]
    ebformat    = config["EbookFormat"]
    smtpserver  = config["SMTPServer"]
    serverport  = config["ServerPort"]
    emailadress = config["EmailAdress"]
    password    = config["EmailAdressPw"]
    starttls    = config["ServerStartSSL"]

    # Load Data from Database
    chapters = helper.getChapters(database)
    users    = helper.getUsers(database)

    # Debug Users:
    logging.debug("Userlist:")
    logging.debug(users)


    # Start conversion loop!
    for chapter in chapters:

        # get relevant data of this Manga
        mangatitle   = chapter[2]
        mangaid      = int(chapter[0])
        issent       = int(chapter[8])
        eblocation   = str(saveloc + mangatitle + "/" + mangatitle + "." + ebformat.lower())

        if issent != 0:
            logging.debug("%s has been sent already!" % mangatitle)
        else:
            logging.info("Sending %s..."% mangatitle)


            for user in users:
                kindle_mail = user[3]
                shouldsend  = user[4]

                # Check if user wants Mails
                if shouldsend == "True":
                    
                    logging.debug("Compiling Email for %s" % user[1])
                    # Compile Email
                    msg = MIMEMultipart()
                    msg['Subject'] = 'Ebook Delivery of %s' % mangatitle
                    msg['Date'] = formatdate(localtime=True)
                    msg['From'] = emailadress
                    msg['To'] = kindle_mail

                    msg.attach(MIMEText("Ebook delivery!"))


                    part = MIMEBase('application', "octet-stream")
                    part.set_payload( open(eblocation,"rb").read() )
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(eblocation)))
                    msg.attach(part)

                    # Connect to Email Server
                    try:
                        server = smtplib.SMTP(smtpserver,serverport)
                        if starttls:
                            server.starttls()
                        server.login(emailadress,password)
                        server.sendmail(emailadress, kindle_mail, msg.as_string())
                        server.quit()
                    except Exception as e:
                        logging.debug("Could not send email! %s" % e)


                    logging.debug("Sent email to %s "% kindle_mail)
                
                # Set Email as Sent
                helper.setIsSent(mangaid,database)
                logging.info("Sent %s..."% mangatitle)




