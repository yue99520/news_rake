import unittest

from getnews.storage.postgres import *

db = DBControl(PostgresqlExtDatabase(
    'gen3_crawler',
    user='user',
    password='password',
    host='localhost',
    port=5432
))


class TestArticleModel(unittest.TestCase):
    def setUp(self):
        db.connect()
        db.create_tables()

    def tearDown(self):
        db.drop_tables()
        db.close()

    def test_article_creation(self):
        Article.create(
            url='https://example.com/article1',
            date='2024-08-17',
            news_pic={'img1': 'https://example.com/image1.jpg'},
            origin_language='en',
            news_topic_eng='Test Topic',
            news_topic_cn='測試主題',
            content_cn='這是中文內容。',
            content_eng='This is English content.'
        )
        result = (Article.select(Article.news_topic_cn, Article.url, Article.date)
                  .where(Article.news_topic_cn == '測試主題')
                  .get())
        self.assertEqual(result.news_topic_cn, '測試主題')
        self.assertEqual(result.url, 'https://example.com/article1')
        self.assertEqual(str(result.date), "2024-08-17")


if __name__ == '__main__':
    unittest.main()
