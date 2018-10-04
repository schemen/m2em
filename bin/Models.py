from peewee import *
import configparser


config_reader = configparser.ConfigParser()
config_reader.read("config.ini")
config = config_reader["CONFIG"]

db = SqliteDatabase(config['Database'])

class ModelBase(Model):
    class Meta:
        database = db

class User(ModelBase):
    email = TextField(null=True)
    name = TextField()
    kindle_mail = TextField(null=True)
    sendtokindle = IntegerField(null=True)
    userid = AutoField()

class Chapter(ModelBase):
    chapter = TextField(null=True)
    chapterid = AutoField()
    date = TextField(null=True)
    desc = TextField(null=True)
    isconverted = IntegerField(null=True)
    ispulled = IntegerField(null=True)
    issent = IntegerField(null=True)
    manganame = TextField(null=True)
    origin = TextField(null=True)
    pages = IntegerField(null=True)
    title = TextField()
    url = TextField()

class Feeds(ModelBase):
    feedid = AutoField()
    url = TextField()

def create_tables():
    db.connection()
    db.create_tables([User, Chapter, Feeds])
