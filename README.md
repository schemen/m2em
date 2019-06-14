# m2em - Manga to eManga

### Foreword
I always had the issue of loving my kindle and ebooks and loving mangas. 

While I buy books/mangas to support the author and have a nice collection, I love & support the e-Format and only read on those as they're are way easier to use.

Not living in Japan has me not really having any readable access of weekly chapters in eManga format, so I wanted to write something to help me out on that!

### Here comes M2EM

M2em let's you automatically download Mangas via RSS Feed that updates at a configurable interval (and comics in the future?), convert them into eMangas and send them off via Email (Target being the Email to Kindle function of Amazon)!

## Supported Websites

* Mangastream
* MangaFox
* Cdmnet

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

## Docker Setup
You can use the Dockerfile or the image schemen/m2em. All options in the config.ini are available as environment variable. Make sure you write the exactly the same!

Example Compose file:
```
version: '2'
services:
  m2em:
    image: schemen/m2em:latest
    environment:
     - SMTPServer=mail.example.com
     - EmailAddress=comic@example.com
     - EmailAddressPw=verysecurepassword
    volumes:
     - <DATA_DIRECTORY>:/usr/src/app/data

``` 

## Concept
As a concept, M2em has different workers that run in a loop. All Chapter/user data is saved in a SQLite3 Database.
* RssParser - Parsing the RSS feed and saving the information of each chapter
* Downloader - Downloading the Mangas and saving them
* Converter - Converting images into ebooks
* Sender - Compiling & Sending Emails to users and marking them as SENT


### The Loop Run & Daemon Loop Run
If you start m2em in loop mode (with or without --daemon) it will only consider any action with elements that that are
younger than 24h hours.

The use of that is having it running on the server 24/7, waiting for updates from the feeds and ONLY handling said updates.

### Direct action
You can start a part of the loop without the restriction of 24h. Use the -a (--action) command with either element you wish to start.

Example: if you wish to download all chapters you have saved in your database, you start the download action.
```
./m2em.py --action downloader
```
### Chapter action
You can directly apply an action to one chapter with the options --download, --convert or --send. You need to pass
the ID of said chapter, you can find that out with "-Lc" or "-lc".
You can pass multiple IDs.

Also, you can process N chapters with the "--process/-p" option:
```
./m2em.py -p 100 #Downloads, Converts and Sends chapter with ID 100
```


```
./m2em.py --download 100 #Downloads chapter with ID 100
```

# Usage

### Help output:
```
usage: m2em.py [-h] [-af ADD_FEED] [-au] [-lm [LIST_MANGA]] [-lc] [-Lc] [-lf]
               [-lu] [-cd] [-s] [--send [SEND [SEND ...]]]
               [--convert [CONVERT [CONVERT ...]]]
               [--download [DOWNLOAD [DOWNLOAD ...]]]
               [-p [PROCESS [PROCESS ...]]] [-a ACTION] [-ss SWITCH_SEND]
               [-dc DELETE_CHAPTER] [-du DELETE_USER] [-df DELETE_FEED]
               [--daemon] [-d] [-v]

Manga to eManga - m2em

optional arguments:
  -h, --help            show this help message and exit
  -af ADD_FEED, --add-feed ADD_FEED
                        Add RSS Feed of Manga. Only Mangastream & MangaFox are
                        supported
  -au, --add-user       Adds new user
  -lm [LIST_MANGA], --list-manga [LIST_MANGA]
                        Lists Manga saved in database. If a Manga is passed,
                        lists chapters to said Manga
  -lc, --list-chapters  Lists the last 10 Chapters
  -Lc, --list-chapters-all
                        Lists all Chapters
  -lf, --list-feeds     Lists all feeds
  -lu, --list-users     Lists all Users
  -cd, --create-db      Creates DB. Uses Configfile for Naming
  -s, --start           Starts one loop
  --send [SEND [SEND ...]]
                        Sends Chapter directly by chapter ID. Multiple IDs can
                        be given
  --convert [CONVERT [CONVERT ...]]
                        Converts Chapter directly by chapter ID. Multiple IDs
                        can be given
  --download [DOWNLOAD [DOWNLOAD ...]]
                        Downloads Chapter directly by chapter ID. Multiple IDs
                        can be given
  -p [PROCESS [PROCESS ...]], --process [PROCESS [PROCESS ...]]
                        Processes chapter(s) by chapter ID, Download, convert,
                        send. Multiple IDs can be given
  -a ACTION, --action ACTION
                        Start action. Options are: rssparser (collecting feed
                        data), downloader, converter or sender
  -ss SWITCH_SEND, --switch-send SWITCH_SEND
                        Pass ID of User. Switches said user Send eBook status
  -dc DELETE_CHAPTER, --delete-chapter DELETE_CHAPTER
                        Pass ID of Chapter. Deletes said Chapter
  -du DELETE_USER, --delete-user DELETE_USER
                        Pass ID of User. Deletes said User
  -df DELETE_FEED, --delete-feed DELETE_FEED
                        Pass ID of Feed. Deletes said Feed
  --daemon              Run as daemon
  -d, --debug           Debug Mode
  -v, --version         show program's version number and exit
  -f "filter_regex", --filter "filter_regex"
                        Adds a filter(python regex format), to filter the
                        title of any manga parsed. Example: "(?i)one-punch"
  -fl, --filter-list    Lists all filters


```

## Initial Data
To have a working environment you need to add some initial data and create the database
```x-sh
./m2em.py --create-db # Create a DB
./m2em.py --add-feed <URL> # Add an RSS Feed you want to pull
# Please note that you should set the sending AFTER a complete run for now
./m2em.py --add-user  # Add a user

```

For the sending to work, you need to have an email account so the program can send from it. I recommend creating a new email account for this. Change the Email settings in the config.ini to be able to use it.

## Config File
```
[CONFIG]
# Location relative to the code position
SaveLocation = data/
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

## Examples

If you want to check out the manga that are in the database:
```
./m2em.py -lm
```
You can use this out put to refine the search! 
If you pass the manga name you get all chapters listed from that manga:
```
./m2em.py -lm "Shokugeki no Souma"
Listing all chapters of Shokugeki no Souma:
ID          MANGA          CHAPTER      CHAPTERNAME               RSS ORIGIN            SEND STATUS
===================================================================================================
112   Shokugeki no Souma   240       Not Cute             https://mangastream.com/rss   SENT

91    Shokugeki no Souma   238       The Queen's Tart     https://mangastream.com/rss   SENT

78    Shokugeki no Souma   239       Her Fighting Style   https://mangastream.com/rss   SENT
```


To start a single run through the workers, you can simply execute the main program:
```
./m2em.py -s
```

If you wish to run the program as a daemon, start it with the option "--daemon" as well. It will re-run at the config "Sleep" in second.
```
./m2em.py -s --daemon
```

If you wish to disable/enable sending status of a user, use the -ss command
```
./m2em.py -ss <USERID>
```


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
* MangaFox has issues with SSL Verification on some systems. For now, Simply add the http feed.

Please Open an issue if you find anything!

# Acknowledgement
I greatly thank Ciro Mattia Gonano and Paweł Jastrzębski that created the KCC Library that enables the automatic conversation into Ebooks that are compatible with all Comic features of the Kindle!
https://github.com/ciromattia/kcc
