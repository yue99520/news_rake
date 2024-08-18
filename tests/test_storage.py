import unittest
from datetime import datetime

from playhouse.postgres_ext import PostgresqlExtDatabase
from getnews.storage import URLBasedIdentifierHelper, DBControl, SpiderContext


db = DBControl(PostgresqlExtDatabase(
    'gen3_crawler',
    user='user',
    password='password',
    host='localhost',
    port=5432
))


class TestURLBasedIdentifierHelper(unittest.TestCase):
    def setUp(self):
        db.connect()
        db.create_tables()
        self.helper = URLBasedIdentifierHelper()

    def tearDown(self):
        db.drop_tables()
        db.close()

    def test_safe_create_article(self):
        article_data = {
            "platform_name": "test_platform",
            "spider_name": "test_spider",
            "url": "https://example.com/news1",
            "date": datetime.now(),
            "news_pic": {"img1": "https://example.com/image1.jpg"},
            "origin_language": "en",
            "news_topic_eng": "Test Topic",
            "news_topic_cn": "測試主題",
            "content_cn": "這是中文內容。",
            "content_eng": "This is English content."
        }
        spider_name = "test_spider"

        # Create an article and check if it was created successfully
        article, created = self.helper.safe_create_article(spider_name, article_data, extra_info={"test": "123"})
        self.assertTrue(created)
        self.assertEqual(article.url, article_data["url"])
        expected_article_id = article.id

        # Try to create the same article again and check that it's not created again
        article, created = self.helper.safe_create_article(spider_name, article_data, extra_info={"test": "456"})
        self.assertFalse(created)

        # Check if the spider context was updated
        context = SpiderContext.get(SpiderContext.spider_name == spider_name)
        self.assertEqual(context.latest_article_id.id, expected_article_id)
        self.assertEqual(context.extra_info, {"test": "123"})

    def test_does_exist(self):
        article_data = {
            "platform_name": "test_platform",
            "spider_name": "test_spider",
            "url": "https://example.com/news2",
            "date": datetime.now(),
            "news_pic": {"img2": "https://example.com/image2.jpg"},
            "origin_language": "en",
            "news_topic_eng": "Another Topic",
            "news_topic_cn": "另一個測試主題",
            "content_cn": "這是另一篇中文內容。",
            "content_eng": "This is another English content."
        }

        # Initially, the article should not exist
        self.assertFalse(self.helper.does_exist(url=article_data["url"]))

        # Create the article
        self.helper.safe_create_article("test_spider", article_data)

        # Now, the article should exist
        self.assertTrue(self.helper.does_exist(url=article_data["url"]))

    def test_get_spider_context_or_none(self):
        spider_name = "test_spider_context"

        # Initially, there should be no context for this spider
        context = self.helper.get_spider_context_or_none(spider_name)
        self.assertIsNone(context)

        # Create an article to generate a context
        article_data = {
            "platform_name": "test_platform",
            "spider_name": spider_name,
            "url": "https://example.com/news3",
            "date": datetime.now(),
            "news_pic": {"img3": "https://example.com/image3.jpg"},
            "origin_language": "en",
            "news_topic_eng": "Third Topic",
            "news_topic_cn": "第三個測試主題",
            "content_cn": "這是第三篇中文內容。",
            "content_eng": "This is the third English content."
        }
        saved_article, created = self.helper.safe_create_article(spider_name, article_data, extra_info={"test": "123"})
        self.assertTrue(created)

        # Now, there should be a context for this spider
        context = self.helper.get_spider_context_or_none(spider_name)
        self.assertIsNotNone(context)
        self.assertEqual(context["spider_name"], spider_name)
        self.assertEqual(context["url"], saved_article.url)
        self.assertEqual(context["latest_article_id"], saved_article.id)
        self.assertEqual(context["news_topic_eng"], saved_article.news_topic_eng)
        self.assertEqual(context["extra_info"], {"test": "123"})


if __name__ == '__main__':
    unittest.main()
