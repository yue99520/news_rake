import abc
import json
import threading
from typing import Tuple, Dict

from getnews.storage import CMSClient


class BaseStorageHelper(abc.ABC):

    @abc.abstractmethod
    def initialize_spider(self, spider_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def safe_create_article(self, spider_name: str, article, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def does_exist(self, item, **kwargs) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_spider_context_or_none(self, spider_name: str) -> dict:
        raise NotImplementedError


class URLBasedIdentifierHelper(BaseStorageHelper):
    CREATE_ARTICLE_LOCK = threading.Lock()

    def __init__(self, cms_client: CMSClient, spider_name: str):
        self.cms_client = cms_client
        self.initialize_spider(spider_name)

    def initialize_spider(self, spider_name: str):
        spider = self.get_spider_context_or_none(spider_name)
        if spider is None:
            spider = self.cms_client.create_spider({
                "spiderName": spider_name,
                "extraInfo": {},
            })
            print("initialize spider: ", json.dumps(spider, indent=2))
        else:
            print("spider is found: ", json.dumps(spider, indent=2))

    def safe_create_article(self, spider_name: str, article, **kwargs) -> Tuple[Dict, bool]:
        if "URL" not in article:
            raise Exception("article must have a url")

        try:
            article["spider"] = {
                "connect": {
                    "spiderName": spider_name,
                }
            }
            spider = {"spiderName": "test_spider2"}

            extra_info = kwargs.get('extra_info')
            if extra_info is not None:
                spider["extraInfo"] = extra_info
            crawler = self.cms_client.create_crawler(crawler=article, spider=spider)
            return crawler, True
        except Exception as e:
            crawler = self.cms_client.get_crawler_or_none(article["URL"])
            if crawler is None:
                raise e
            return crawler, False

    def does_exist(self, **kwargs) -> bool:
        if "url" not in kwargs:
            raise Exception("item must have a url")
        return self.cms_client.get_crawler_or_none(kwargs['url'])

    def get_spider_context_or_none(self, spider_name: str) -> dict:
        if not spider_name:
            raise Exception("spider_name must be provided")
        return self.cms_client.get_spider_or_none(spider_name)


class SolanaNewsStorageHelper(URLBasedIdentifierHelper):
    pass


class SolanaMediumStorageHelper(URLBasedIdentifierHelper):
    pass


class TheBlockStorageHelper(URLBasedIdentifierHelper):
    pass


class ForesightStorageHelper(URLBasedIdentifierHelper):
    pass


class FollowinStorageHelper(URLBasedIdentifierHelper):
    pass


class JinseStorageHelper(URLBasedIdentifierHelper):
    pass


class CoindeskStorageHelper(URLBasedIdentifierHelper):
    pass


class ZombitStorageHelper(URLBasedIdentifierHelper):
    pass


class DecryptStorageHelper(URLBasedIdentifierHelper):
    pass
