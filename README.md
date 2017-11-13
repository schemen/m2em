# m2em
Manga to eManga

## Add a user


## Add a Feed that gets pulled


## How to send it to the Kindle
Currently, there is an issue of Amazon not accepting any emails directly sent by this (And other cli programs I've tested).
As a workaround and you requiring an accessible email adress anyway, you can create imap filter that redirects all
received messages to your Kindle email.


## Create and install virtual environment
```x-sh
virtualenv venv
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