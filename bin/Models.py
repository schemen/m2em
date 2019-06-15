""" Models Module """
from peewee import *
import bin.Config as Config


# Load config right at the start
config = Config.load_config()

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

class Migratehistory(ModelBase):
    id = AutoField()
    name = CharField()
    migrated_at = DateTimeField()

def create_tables():
    db.connection()
    db.create_tables([User, Chapter, Feeds])
