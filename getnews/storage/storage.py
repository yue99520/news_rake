import abc
from datetime import datetime
from typing import Tuple

from .postgres import Article, SpiderContext


class BaseStorageHelper(abc.ABC):
    @abc.abstractmethod
    def safe_create_article(self, spider_name: str, article) -> Tuple[bool, Article]:
        raise NotImplementedError

    @abc.abstractmethod
    def does_exist(self, item, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get_spider_context_or_none(self, spider_name: str) -> dict:
        raise NotImplementedError


class URLBasedIdentifierHelper(BaseStorageHelper):

    def safe_create_article(self, spider_name: str, article) -> Tuple[Article, bool]:
        """
        Atomically create a new article and update the context of the spider.
        return (remote_article, created)
        """
        if "url" not in article:
            raise Exception("article must have a url")
        with Article.get_db().atomic():
            remote_article = Article.get_or_none(Article.url == article["url"])
            if remote_article is not None:
                return remote_article, False

            remote_article = Article.create(**article)
            context = {
                "spider_name": spider_name,
                "latest_article_id": remote_article.id,
                "extra_info": {},
                "updated_at": datetime.now()
            }
            remote_context = SpiderContext.get_or_none(SpiderContext.spider_name == spider_name)
            if remote_context is None:
                SpiderContext.create(**context)
            else:
                remote_context.latest_article_id = remote_article.id
                remote_context.extra_info = context["extra_info"]
                remote_context.updated_at = context["updated_at"]
                remote_context.save()

            return remote_article, True

    def does_exist(self, **kwargs):
        if "url" not in kwargs:
            raise Exception("item must have a url")
        return Article.select().where(Article.url == kwargs['url']).exists()

    def get_spider_context_or_none(self, spider_name: str) -> dict:
        if not spider_name:
            raise Exception("spider_name must be provided")
        query = (SpiderContext.select(SpiderContext, Article)
                 .join(Article, on=(SpiderContext.latest_article_id == Article.id))
                 .where(SpiderContext.spider_name == spider_name))
        return query.dicts().first()


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
