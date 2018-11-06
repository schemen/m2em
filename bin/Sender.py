""" Sending Module """
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate, make_msgid
from email.generator import Generator
from email import encoders
import bin.Config as Config
import bin.Helper as helper

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Sender:
    """ Class that takes care of sending the ebooks to the users! """

    def __init__(self):
        self.saveloc = None
        self.ebformat = None
        self.mangatitle = None
        self.manganame = None
        self.eblocation = None
        self.chapterdate = None
        self.smtpserver = None
        self.serverport = None
        self.emailadress = None
        self.password = None
        self.starttls = None
        self.mangaid = None
        self.issent = None
        self.chapterdate = None

        # Will be defined by handler
        self.users = None
        self.database = None



    def data_collector(self, chapter):
        """ Method that gathers data required for this class """

        # Load config right at the start
        config = None
        if not config:
            config = Config.load_config()

        # Load configs required here
        self.saveloc = config["SaveLocation"]
        self.ebformat = config["EbookFormat"]
        self.smtpserver = config["SMTPServer"]
        self.serverport = config["ServerPort"]
        self.emailadress = config["EmailAddress"]
        self.password = config["EmailAddressPw"]
        self.starttls = config["ServerStartSSL"]


        # get relevant data of this Manga
        self.mangatitle = chapter.title
        self.chapterdate = chapter.date
        self.mangaid = int(chapter.chapterid)
        self.issent = int(chapter.issent)
        self.manganame = chapter.manganame

        # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
        self.mangatitle = helper.sanetizeName(self.mangatitle)
        self.manganame = helper.sanetizeName(self.manganame)


        self.eblocation = str(self.saveloc + self.manganame + "/" + self.mangatitle + "/" +
                              self.mangatitle + "." + self.ebformat.lower())

        # Initialize emtpy Users table
        self.users = []





    def send_eb(self):
        """ Method that sends data to the user! """

        # Iterate through user
        for user in self.users:
            kindle_mail = user.kindle_mail
            shouldsend = user.sendtokindle
            user_mail = user.email

            # Check if user wants Mails
            if shouldsend == 1:

                logging.debug("Compiling Email for %s", user.name)


                # Compile Email
                msg = MIMEMultipart()
                msg['Subject'] = 'Ebook Delivery of %s' % self.mangatitle
                msg['Date'] = formatdate(localtime=True)
                msg['From'] = self.emailadress
                msg['To'] = kindle_mail
                msg['Message-ID'] = make_msgid()

                text = "Automatic Ebook delivery by m2em."
                msg.attach(MIMEText(text))


                # Add Ebook as attachment
                ebfile = open(self.eblocation, 'rb')

                attachment = MIMEBase('application', 'octet-stream',
                                      name=os.path.basename(self.eblocation))
                attachment.set_payload(ebfile.read())
                ebfile.close()
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment',
                                      filename=os.path.basename(self.eblocation))

                msg.attach(attachment)

                # Convert message to string
                sio = StringIO()
                gen = Generator(sio, mangle_from_=False)
                gen.flatten(msg)
                msg = sio.getvalue()

                # Send Email Off!
                # Debug Server Data
                logging.debug("Server: %s", self.smtpserver)
                logging.debug("Port: %s", self.serverport)

                try:
                    server = smtplib.SMTP(self.smtpserver, self.serverport,)
                    if self.starttls:
                        server.starttls()
                    server.ehlo()
                    server.login(self.emailadress, self.password)
                    #server.sendmail(emailadress, kindle_mail, msg.as_string())
                    server.sendmail(self.emailadress, kindle_mail, msg)
                    server.close()
                    logging.debug("Sent Ebook email to %s ", kindle_mail)
                    self.send_confirmation(user_mail)
                except smtplib.SMTPException as fail:
                    logging.debug("Could not send email! %s", fail)

        # Set Email as Sent
        helper.setIsSent(self.mangaid)
        logging.info("Sent %s to all requested users.", self.mangatitle)


    def send_confirmation(self, usermail):
        """ Method to send a confirmation mail to the user """

        # Compile Email
        msg = MIMEMultipart()
        msg['Subject'] = 'Ebook Delivery of %s' % self.mangatitle
        msg['Date'] = formatdate(localtime=True)
        msg['From'] = self.emailadress
        msg['To'] = usermail
        msg['Message-ID'] = make_msgid()

        text = '%s has been delivered to your Kindle Email!' % self.mangatitle
        msg.attach(MIMEText(text))

        # Convert message to string
        sio = StringIO()
        gen = Generator(sio, mangle_from_=False)
        gen.flatten(msg)
        msg = sio.getvalue()

        try:
            server = smtplib.SMTP(self.smtpserver, self.serverport, )
            if self.starttls:
                server.starttls()
            server.ehlo()
            server.login(self.emailadress, self.password)
            server.sendmail(self.emailadress, usermail, msg)
            server.close()
            logging.debug("Sent confirmation email to %s ", usermail)
        except smtplib.SMTPException as fail:
            logging.debug("Could not send email! %s", fail)
