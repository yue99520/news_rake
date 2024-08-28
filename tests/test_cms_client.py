import os
import unittest

from dotenv import load_dotenv

from getnews.storage import CMSClient

load_dotenv()


class TestCMSClient(unittest.TestCase):
    def setUp(self):
        self.client = CMSClient(
            graphql_endpoint="https://cms.gen3.network/api/graphql",
            identity=os.getenv('CMS_IDENTITY'),
            secret=os.getenv('CMS_PASSWORD')
        )
        assert self.client.login()

    def test_create_and_get_crawler(self):
        new_crawler = self.client.create_crawler(
            crawler={
                "URL": "https://example.com/news3",
                "date": "2024-08-26T15:00:00.000Z",
                "newsPic": "",
                "language": "en",
                "platformName": "test_platform",
                # "spiderName": "test_spider",
                "newsTopicCN": "測試主題",
                "newsTopicEN": "Test Topic",
                "contentCN": "這是中文內容。",
                "contentEN": "This is English content.",
                "spider": {
                    "connect": {
                        "spiderName": "test_spider2",
                    }
                },
            }, spider={
                "spiderName": "test_spider2",
                "extraInfo": {"test": "123"},
                "updatedAt": "2024-08-26T15:00:00.000Z",
            })
        print("created: ", new_crawler)
        crawler = self.client.get_crawler_or_none(new_crawler["URL"])
        print("get: ", crawler)
        crawler = self.client.delete_crawler(new_crawler["URL"])
        print("deleted: ", crawler)
        self.assertIsNotNone(crawler)
        crawler = self.client.get_crawler_or_none(new_crawler["URL"])
        self.assertIsNone(crawler)

    def test_create_spider_and_get(self):
        new_spider = self.client.create_spider({
            "spiderName": "test_spider2",
            "extraInfo": {},
        })

        print("created: ", new_spider)
        spider = self.client.get_spider_or_none("test_spider2")
        print("get: ", spider)
