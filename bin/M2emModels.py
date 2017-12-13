from peewee import *


database = SqliteDatabase('main.1.db')


class BaseModel(Model):
    class Meta:
        database = database

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


class Feed(BaseModel):
    feedid = PrimaryKeyField()
    url = CharField()

    class Meta:
        order_by = ('feedid',)

def create_tables():
    database.connect()
    database.create_tables([User, Chapter, Feed])
