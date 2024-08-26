import abc
from datetime import datetime
from typing import Tuple
import requests
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
    def graphql_query(self, query: str, variables: dict):
        response = requests.post(
            "https://cms.gen3.network/api/graphql",
            json={"query": query, "variables": variables},
            headers=self.headers
        )
        return response.json()
    
    def safe_create_article(self, spider_name: str, article, **kwargs) -> Tuple[bool]:
        pass
        # if "url" not in article:
        #     raise Exception("article must have a url")
        # existing_crawler_query = """
        # query ($where: CrawlerWhereInput) {
        #   items: crawlers(where: $where, take: 1, skip: 0) {
        #     id
        #     URL
        #   }
        # }
        # """
        # variables = {
        #     "where": {
        #         "URL": {"equals": article["url"]}
        #     }
        # }

        # return  True

    def does_exist(self, **kwargs) -> bool:
        pass
        # if "url" not in kwargs:
        #     raise Exception("item must have a url")
        # return Article.select().where(Article.url == kwargs['url']).exists()

    def get_spider_context_or_none(self, spider_name: str) -> dict:
        pass
        # if not spider_name:
        #     raise Exception("spider_name must be provided")
        # query = (SpiderContext.select(SpiderContext, Article)
        #          .join(Article, on=(SpiderContext.latest_article_id == Article.id))
        #          .where(SpiderContext.spider_name == spider_name))
        # return query.dicts().first()


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
