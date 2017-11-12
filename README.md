# m2em
Manga to eManga

## Create and install virtual environment
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

## dependencies
* validators
* texttable
* requests
* bs4
* urllib3
* feedparser
* KindleComicConverter


## Optional dependencies
* KindleGen v2.9+ in a directory reachable by your PATH or in KCC directory (For MOBI generation)