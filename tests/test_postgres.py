import json
import unittest

from getnews.spiders import SolanaNewsSpider
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
            platform_name="test_platform",
            spider_name="test_spider",
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

    def test_get_spider_context(self):
        article = Article.create(
            url='https://example.com/article1',
            platform_name="test_platform",
            spider_name="test_spider",
            date='2024-08-17',
            news_pic={'img1': 'https://example.com/image1.jpg'},
            origin_language='en',
            news_topic_eng='Test Topic',
            news_topic_cn='測試主題',
            content_cn='這是中文內容。',
            content_eng='This is English content.'
        )
        SpiderContext.get_or_create(spider_name=SolanaNewsSpider.name, defaults={
            "spider_name": SolanaNewsSpider.name,
            "latest_article_id": article.id,
            "extra_info": {"test": "123"},
        })
        query = (SpiderContext.select(SpiderContext, Article)
                 .join(Article, on=(SpiderContext.latest_article_id == Article.id))
                 .where(SpiderContext.spider_name == SolanaNewsSpider.name))
        data = query.dicts().get()
        assert data['extra_info']['test'] == '123'
        assert data['url'] == 'https://example.com/article1'
        assert data['updated_at'] is not None


if __name__ == '__main__':
    unittest.main()
