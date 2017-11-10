import  sqlite3
import feedparser

# Get all current feeds
# Currently hardcoded for testing
feedurl = "https://mangastream.com/rss"
feed = feedparser.parse(feedurl)

# Open Database
conn = sqlite3.connect("test.db")
c = conn.cursor()


for entry in feed.entries:



    article_title = entry.title
    article_link = entry.link
    article_pubDate = entry.published
    article_description = entry.description

    data = [({feedurl},{article_title},{article_pubDate},{article_link},{article_description},"False","False","False",0,0,'')]

    print "{} [{}]".format(article_title, article_description)
    print "Released at {}".format(article_pubDate)
    print "URL: {}".format(article_link)
    print data

    # c.execute("INSERT INTO chapters (origin,title,date,url,desc,ispulled,isconverted,issent,pages,chapter,manganame) values ({feedurl},{article_title},{article_pubDate},{article_link},{article_description},"False","False","False",0,0,'')")
    conn.commit()

conn.close()

#
# c.execute("INSERT INTO chapters ({idf}, {cn}) VALUES (123456, 'test')".\
#         format(tn=table_name, idf=id_column, cn=column_name))
