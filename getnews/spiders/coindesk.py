import scrapy
from scrapy.http import XmlResponse, HtmlResponse

from getnews.utils.clean_utils import CleanUtils


class CoindeskSpider(scrapy.Spider):
    name = "coindesk"
    allowed_domains = ["www.coindesk.com"]
    start_urls = ["https://www.coindesk.com/arc/outboundfeeds/news-sitemap-index-es/"]

    custom_settings = {
        'DELAY_REQUEST': 0.3,
        'CONCURRENT_REQUESTS': 2,
    }

    def parse(self, response, **kwargs):
        if not isinstance(response, XmlResponse):
            self.logger.error(f"Response is not XmlResponse: {response} ({response.url})")
            return
        for url, lastmod in self.parse_sitemap(response):
            url = url.replace("/es", "")
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
        title = response.xpath('//title/text()').get()
        paragraphs = response.xpath(f'//div[@data-submodule-name="composer-content"]//p').getall()
        content = CoindeskSpider.__content_cleaning_and_rebuilding(paragraphs)

        yield {
            'url': article_url,
            'platform': CoindeskSpider.name,
            'date': article_date,
            'title': title,
            'content': content
        }

    @staticmethod
    def __content_cleaning_and_rebuilding(paragraphs):
        clean_paragraphs = list()
        for paragraph in paragraphs:
            paragraph = CleanUtils.remove_tags(paragraph, ['section', 'style', 'script'])
            paragraph = CleanUtils.convert_weird_chars(paragraph) if paragraph != '' else ''
            paragraph = CleanUtils.clean_attributes(paragraph) if paragraph != '' else ''
            if paragraph != '':
                clean_paragraphs.append(paragraph)
        return '<div>' + ''.join(clean_paragraphs) + '</div>'
