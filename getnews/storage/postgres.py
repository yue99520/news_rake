from playhouse.postgres_ext import *


db_proxy = Proxy()


class Article(Model):
    id = AutoField()
    url = CharField(unique=True)
    date = DateField()
    news_pic = BinaryJSONField()
    origin_language = CharField()
    news_topic_eng = CharField()
    news_topic_cn = CharField()
    content_cn = TextField()
    content_eng = TextField()

    class Meta:
        database = db_proxy
        table_name = 'articles'


class DBControl:
    TABLES = [Article]

    def __init__(self, db):
        self.db = db
        db_proxy.initialize(db)

    def create_tables(self):
        self.db.create_tables(self.TABLES)

    def drop_tables(self):
        self.db.drop_tables(self.TABLES)

    def connect(self):
        self.db.connect()

    def close(self):
        self.db.close()
