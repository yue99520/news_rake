import abc
from typing import Tuple

from .postgres import Article


class BaseStorageHelper(abc.ABC):
    @abc.abstractmethod
    def safe_create_article(self, article) -> Tuple[bool, Article]:
        raise NotImplementedError

    @abc.abstractmethod
    def does_exist(self, item, **kwargs):
        raise NotImplementedError


class URLBasedIdentifierHelper(BaseStorageHelper):

    def safe_create_article(self, article) -> Tuple[Article, bool]:
        if "url" not in article:
            raise Exception("article must have a url")
        return Article.get_or_create(url=article["url"], defaults=article)

    def does_exist(self, **kwargs):
        if "url" not in kwargs:
            raise Exception("item must have a url")
        return Article.select().where(Article.url == kwargs['url']).exists()


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


class JinseStorageHelper(BaseStorageHelper):
    def safe_create_article(self, article) -> Tuple[bool, Article]:
        return super().safe_create_article(article)

    def does_exist(self, item, **kwargs):
        return super().does_exist(item, **kwargs)


class CoindeskStorageHelper(URLBasedIdentifierHelper):
    pass


class ZombitStorageHelper(URLBasedIdentifierHelper):
    pass


class DecryptStorageHelper(URLBasedIdentifierHelper):
    pass
