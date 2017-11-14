import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate, make_msgid
from email.generator import Generator
from email import encoders
import bin.m2emHelper as helper

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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

    # Debug Server Data
    logging.debug("Server: %s" % smtpserver)
    logging.debug("Port: %s" % serverport)

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
                    msg['Message-ID'] = make_msgid()

                    text = "Automatic Ebook delivery by m2em."
                    msg.attach(MIMEText(text))


                    # Add Ebook as attachment
                    ebfile = open(eblocation, 'rb')

                    attachment = MIMEBase('application', 'octet-stream', name=os.path.basename(eblocation))
                    attachment.set_payload(ebfile.read())
                    ebfile.close()
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment',
                                  filename=os.path.basename(eblocation))
                    
                    msg.attach(attachment)

                    # Convert message to string
                    sio = StringIO()
                    gen = Generator(sio, mangle_from_=False)
                    gen.flatten(msg)
                    msg = sio.getvalue()

                    # Send Email Off!
                    try:
                        server = smtplib.SMTP(smtpserver,serverport,)
                        if starttls:
                            server.starttls()
                        server.ehlo()
                        server.login(emailadress,password)
                        #server.sendmail(emailadress, kindle_mail, msg.as_string())
                        server.sendmail(emailadress, kindle_mail, msg)
                        server.close()
                        logging.debug("Sent email to %s "% kindle_mail)
                    except smtplib.SMTPException as e:
                        logging.debug("Could not send email! %s" % e)

                
            # Set Email as Sent
            helper.setIsSent(mangaid,database)
            logging.info("Sent %s to all requested users."% mangatitle)




