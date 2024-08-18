from typing import Iterable
import scrapy
from markdownify import markdownify

from getnews.storage import ZombitStorageHelper


class ZombitSpider(scrapy.Spider):
    name = "zombit"
    allowed_domains = ["zombit.info"]
    start_urls = ["https://zombit.info/"]
    storage_helper = ZombitStorageHelper()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        articles = response.xpath('//div[@class="post-item row mb-4"]')

        for article in articles:
            title = article.xpath('.//h3[@class="post-title max-two-lines"]/a/text()').get()
            date = article.xpath('.//div[@class="post-date"]/text()').get()
            link_url = article.xpath('.//h3[@class="post-title max-two-lines"]/a/@href').get()
            if link_url:
                link_url = response.urljoin(link_url)
                print('link_url',link_url)
            if self.storage_helper.does_exist(url=link_url):
                continue
            yield scrapy.Request(link_url, callback=self.parse_news, meta={'lastmod': date, 'title': title})

    def parse_news(self, response):
        article_url = response.url
        article_date = response.meta['lastmod']
        title = response.meta['title']
        paragraphs = response.xpath('//div[@class="entry-content"]').getall()
        content = self._content_cleaning_and_rebuilding(paragraphs)

        yield {
            'url': article_url,
            'platform': self.name,
            'date': article_date,
            'title': title,
            'content': content,
            'language': 'zh_tw',
            'images': [],
        }

    @staticmethod
    def _content_cleaning_and_rebuilding(paragraphs):
        clean_paragraphs = []
        for paragraph in paragraphs:
            paragraph = markdownify(paragraph, heading_style="ATX")
            if paragraph.strip():
                clean_paragraphs.append(paragraph)
        return '\n\n'.join(clean_paragraphs)