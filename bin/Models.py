from peewee import *
import configparser


config_reader = configparser.ConfigParser()
config_reader.read("config.ini")
config = config_reader["CONFIG"]

db = SqliteDatabase(config['Database'])

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = TextField(null=True)
    name = TextField()
    kindle_mail = TextField(null=True)
    sendtokindle = IntegerField(null=True)
    userid = PrimaryKeyField()

    class Meta:
        order_by = ('userid',)


class Chapter(BaseModel):
    chapter = IntegerField(null=True)
    chapterid = PrimaryKeyField()
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

    class Meta:
        order_by = ('chapterid',)


class Feeds(BaseModel):
    feedid = PrimaryKeyField()
    url = TextField()

    class Meta:
        order_by = ('feedid',)

def create_tables():
    db.get_conn()
    db.create_tables([User, Chapter, Feeds])
