import scrapy
from scrapy.http import XmlResponse, HtmlResponse
from markdownify import markdownify

from getnews.storage import FollowinStorageHelper


class FollowinSpider(scrapy.Spider):
    name = "followin"
    allowed_domains = ["followin.io"]
    start_urls = ["https://followin.io/unknow/sitemap/news.xml"]
    storage_helper = FollowinStorageHelper()
    # languages = ["zh-Hant", "en"]
    custom_settings = {
        'DELAY_REQUEST': 0.5,
        'CONCURRENT_REQUESTS': 2,
    }

    def parse(self, response, **kwargs):
        if not isinstance(response, XmlResponse):
            self.logger.error(f"Response is not XmlResponse: {response} ({response.url})")
            return
        for url, lastmod in self.parse_sitemap(response):
            url = url.replace("unknow", "zh-Hant")
            if self.storage_helper.does_exist(url=url):
                continue
            yield scrapy.Request(url, callback=self.parse_news, meta={'lastmod': lastmod})

    @staticmethod
    def parse_sitemap(response: XmlResponse):
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        url_nodes = response.xpath('//ns:url', namespaces=namespaces)
        for url_node in url_nodes:
            url = url_node.xpath('ns:loc/text()', namespaces=namespaces).get()
            lastmod = url_node.xpath('ns:lastmod/text()', namespaces=namespaces).get()
            yield url, lastmod

    @staticmethod
    def parse_news(response: HtmlResponse):
        article_url = response.url
        article_date = response.meta['lastmod']
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//*[@id="article-content"]').get()
        content = markdownify(content, heading_style="ATX")
        yield {
            'url': article_url,
            'platform': FollowinSpider.name,
            'date': article_date,
            'title': title,
            'content': content,
            'language': 'zh_tw',
        }
