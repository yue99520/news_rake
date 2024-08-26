import scrapy
from scrapy.http import XmlResponse, HtmlResponse
from markdownify import markdownify

from getnews.storage import CoindeskStorageHelper


class CoindeskSpider(scrapy.Spider):
    name = "coindesk"
    allowed_domains = ["www.coindesk.com"]
    start_urls = ["https://www.coindesk.com/arc/outboundfeeds/news-sitemap-index-es/"]
    storage_helper = CoindeskStorageHelper()

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
        title = response.xpath('//title/text()').get()
        paragraphs = response.xpath(f'//div[@data-submodule-name="composer-content"]//p').getall()
        content = CoindeskSpider.__content_cleaning_and_rebuilding(paragraphs)
        img_urls = CoindeskSpider.__get_all_img_urls(response)

        yield {
            'url': article_url,
            'platform': CoindeskSpider.name,
            'date': article_date,
            'title': title,
            'content': content,
            'language': 'en',
            'images' : img_urls
        }

    @staticmethod
    def __content_cleaning_and_rebuilding(paragraphs):
        clean_paragraphs = list()
        for paragraph in paragraphs:
            paragraph = markdownify(paragraph, heading_style="ATX")
            if paragraph != '':
                clean_paragraphs.append(paragraph)
        return ''.join(clean_paragraphs)

    @staticmethod    
    def __get_all_img_urls(response):
        
        image_urls = response.css('picture img::attr(src)').getall()

        if not image_urls:
            image_urls = []

        return image_urls
        
