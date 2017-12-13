from peewee import *

database = SqliteDatabase('test.db')

class BaseModel(Model):
    class Meta:
        database = database
        
        def to_dict():
        pass

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
        db_table = 'chapter'

class Feeds(BaseModel):
    feedid = PrimaryKeyField()
    url = TextField()

    class Meta:
        db_table = 'feeds'

class User(BaseModel):
    email = TextField(db_column='Email', null=True)
    name = TextField(db_column='Name')
    kindle_mail = TextField(null=True)
    sendtokindle = IntegerField(db_column='sendToKindle', null=True)
    userid = PrimaryKeyField()

    class Meta:
        db_table = 'user'

def create_tables():
    database.connect()
    database.create_tables([User, Chapter, Feed])


