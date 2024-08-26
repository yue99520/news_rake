import abc
import copy
import threading
from datetime import datetime, timezone
from typing import Tuple, Dict

from getnews.storage import CMSClient


class BaseStorageHelper(abc.ABC):
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

    def __init__(self, cms_client: CMSClient):
        self.cms_client = cms_client
    
    def safe_create_article(self, spider_name: str, article, **kwargs) -> Tuple[Dict, bool]:
        if "URL" not in article:
            raise Exception("article must have a url")

        remote_crawler = self.cms_client.get_crawler_or_none(article["URL"])
        if remote_crawler is not None:
            return remote_crawler, False

        remote_context = self.cms_client.get_spider_context_or_none(spider_name)
        with self.CREATE_ARTICLE_LOCK:
            try:
                remote_crawler = self.cms_client.create_crawler(article)
                if remote_crawler is None:
                    raise Exception("Create crawler failed: " + article["URL"])
                now = datetime.now().astimezone(timezone.utc).isoformat() + "Z"
                if remote_context is None:
                    self.cms_client.update_spider_context(spider_name, {
                        "spiderName": spider_name,
                        "latestArticle": remote_crawler,
                        "extraInfo": kwargs.get('extra_info', {}),
                        "updatedAt": now
                    })
                else:
                    remote_context["extraInfo"] = kwargs.get('extra_info', remote_context["extraInfo"])
                    remote_context["latestArticleId"] = remote_crawler["CID"]
                    remote_context["updatedAt"] = now
                    self.cms_client.create_spider_context(remote_context)

                return remote_crawler, True
            except Exception as e:
                if remote_crawler is not None:
                    self.cms_client.delete_crawler(remote_crawler["CID"])
                raise e

    def does_exist(self, **kwargs) -> bool:
        if "url" not in kwargs:
            raise Exception("item must have a url")
        return self.cms_client.get_crawler_or_none(kwargs['url'])

    def get_spider_context_or_none(self, spider_name: str) -> dict:
        if not spider_name:
            raise Exception("spider_name must be provided")
        return self.cms_client.get_spider_context_or_none(spider_name)


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
