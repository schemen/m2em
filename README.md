# m2em - Manga to eManga

### Foreword
I always had the issue of loving my kindle and ebooks and loving mangas. 

While I buy books/mangas to support the author and have a nice collection, I am a very big support of the e-Format and only read on those.

Not living in Japan has me not really having any readable access of weekly chapters in eManga format, so I wanted to write something to help me out on that!

### Here comes M2EM

M2em let's you automatically download Mangas via RSS Feed that updates at a configurable interval (and comics in the future?), convert them into eMangas and send them off via Email (Target being the Email to Kindle function of Amazon)!

# Setup

M2em requires Python3 and I highly recommend working in a virtualenv. Some OS require the python-dev package!

## Create and install virtual environment
```x-sh
git clone git@github.com:schemen/m2em.git && cd m2em
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## dependencies
* validators
* texttable
* requests
* bs4
* urllib3
* feedparser
* KindleComicConverter


## Optional dependencies
* KindleGen v2.9+ in a directory reachable by your PATH or in KCC directory (For MOBI generation). For Windows, place the .exe in the same directory

Get Kindlegen here: https://www.amazon.com/gp/feature.html?docId=1000765211

## Concept
As a concept, M2em has different workers that run in a loop. All Chapter/user data is saved in a SQLite3 Database.
* RssParser - Parsing the RSS feed and saving the information of each chapter
* Downloader - Downloading the Mangas and saving them
* Converter - Converting images into ebooks
* Sender - Compiling & Sending Emails to users and marking them as SENT

With the sourceparser you can add support of a Webhost.

## Supported Websites
Only Mangastream as of now (Mangafox is in the works)

# Usage

### Help output:
```
usage: m2em.py [-h] [-r RSS_FEED] [-u] [-l] [-L] [--list-feeds] [--list-users]
               [-cd] [-s SWITCH_SEND] [-S SWITCH_CHAPTER] [-dc DELETE_CHAPTER]
               [-du DELETE_USER] [-df DELETE_FEED] [--daemon] [-d]

Manga to eManga - m2em

optional arguments:
  -h, --help            show this help message and exit
  -r RSS_FEED, --rss-feed RSS_FEED
                        Add RSS Feed of Manga. Only Mangastream & MangaFox are
                        supported
  -u, --add-user        Adds new user
  -l, --list-chapters   Lists the last 10 Chapters
  -L, --list-chapters-all
                        Lists all Chapters
  --list-feeds          Lists all feeds
  --list-users          Lists all Users
  -cd, --create-db      Creates DB. Uses Configfile for Naming
  -s SWITCH_SEND, --switch-send SWITCH_SEND
                        Pass ID of User. Switches said user Send eBook status
  -S SWITCH_CHAPTER, --switch-chapter SWITCH_CHAPTER
                        Pass ID of Chapter. Switches said Chapter Sent status
  -dc DELETE_CHAPTER, --delete-chapter DELETE_CHAPTER
                        Pass ID of Chapter. Deletes said Chapter
  -du DELETE_USER, --delete-user DELETE_USER
                        Pass ID of User. Deletes said User
  -df DELETE_FEED, --delete-feed DELETE_FEED
                        Pass ID of Feed. Deletes said Feed
  --daemon              Run as daemon
  -d, --debug           Debug Mode
```

## Initial Data
To have a working environment you need to add some initial data and create the database
```x-sh
./m2em.py --create-db # Create a DB
./m2em.py --rss-feed <URL> # Add an RSS Feed you want to pull
./m2em.py --add-user  # Add a user

```

For the sending to work, you need to have an email account so the program can send from it. I recommend creating a new email account for this. Change the Email settings in the config.ini to be able to use it.

## Config File
```
[CONFIG]
# Location relative to the code position
SaveLocation = comic/
# Database name
Database = main.db
# Duration the program sleeps after one run is finished in seconds
Sleep = 900
# Ebook output Format, check
# https://github.com/ciromattia/kcc for more information
EbookFormat = MOBI
# Ebook Profile setting, check 
# https://github.com/ciromattia/kcc for more information
EbookProfile = KV
# Sender Email Server Settings
SMTPServer = mail.example.com
ServerPort = 587
EmailAdress = comic@example.com
EmailAdressPw = yourpassword
ServerStartSSL = True
```



To start a single run through the workers, you can simply execute the main program:
```
./m2em.py
```

If you wish to run the program as a daemon, start it with the option "--daemon". It will re-run at the config "Sleep" in second.


### A complete run with nothing happening:
```
Starting Loop at 2017-11-15 18:13:05
Starting RSS Data Fetcher!
Checking for new Feed Data...
Getting Feeds for https://mangastream.com/rss
Finished Loading RSS Data
Starting all outstanding Chapter Downloads!
Finished all outstanding Chapter Downloads
Starting recursive image conversion!
Finished recursive image conversion!
Starting to send all ebooks!
Finished sending ebooks!
```

## Other
Everything else should be self-explanatory with the "-h" option.

## Known Issues
* Mangafox is not yet supported, in the works
* None other so far

Please Open an issue if you find anything!

# Acknowledgement
I greatly thank Ciro Mattia Gonano and Paweł Jastrzębski that created the KCC Library that enables the automatic conversation into Ebooks that are compatible with all Comic features of the Kindle!
https://github.com/ciromattia/kcc
