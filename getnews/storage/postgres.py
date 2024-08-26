# from datetime import datetime

# from playhouse.postgres_ext import *


# db_proxy = Proxy()


# class Article(Model):
#     id = AutoField()
#     platform_name = CharField()
#     spider_name = CharField()
#     url = CharField(unique=True)
#     date = DateField()
#     news_pic = BinaryJSONField()
#     origin_language = CharField()
#     news_topic_eng = CharField()
#     news_topic_cn = CharField()
#     content_cn = TextField()
#     content_eng = TextField()

#     class Meta:
#         database = db_proxy
#         table_name = 'articles'

#     @classmethod
#     def get_db(cls):
#         return cls._meta.database


# class SpiderContext(Model):
#     id = AutoField()
#     spider_name = CharField(unique=True)
#     latest_article_id = ForeignKeyField(Article, field='id', null=True)
#     extra_info = BinaryJSONField()
#     updated_at = DateTimeField(default=datetime.now())

#     class Meta:
#         database = db_proxy
#         table_name = 'spider_context'

#     @classmethod
#     def get_db(cls):
#         return cls._meta.database


# class DBControl:
#     TABLES = [Article, SpiderContext]

#     def __init__(self, db):
#         self.db = db
#         db_proxy.initialize(db)

#     def create_tables(self):
#         self.db.create_tables(self.TABLES)

#     def drop_tables(self):
#         self.db.drop_tables(self.TABLES)

#     def connect(self):
#         self.db.connect()

#     def close(self):
#         self.db.close()
