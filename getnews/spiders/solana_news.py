from typing import List

import scrapy
from scrapy.selector import SelectorList
from markdownify import markdownify

from getnews.storage import SolanaNewsStorageHelper
from getnews.utils.time_utils import TimeUtils

SOLANA_FQDN = "solana.com"


class SolanaNewsSpider(scrapy.Spider):
    name = "solana_news"
    allowed_domains = [SOLANA_FQDN]
    start_urls = [f"https://{SOLANA_FQDN}/news"]

    def __init__(self, cms_client, *args, **kwargs):
        super(SolanaNewsSpider, self).__init__(*args, **kwargs)
        self.storage_helper = SolanaNewsStorageHelper(cms_client, self.name)

    def parse(self, response, **kwargs):
        for element in self.__get_news_link_elements(response):
            article_path = element.xpath('@href').get()
            article_url = f"https://{SOLANA_FQDN}{article_path}"
            if self.storage_helper.does_exist(url=article_url):
                continue
            yield scrapy.Request(article_url, callback=self._parse_article, meta={'url': article_path})

    def _parse_article(self, response):
        article_url = f"https://{SOLANA_FQDN}" + str(response.meta['url'])
        article_date = response.xpath('/html/head/meta[11]/@content').get()
        article_date = TimeUtils.convert_datetime_to_iso8601(article_date, "%d %B %Y")
        title = response.xpath('//*[@id="__next"]/main/div[2]/section/div/div/div[1]/h1/text()').get()
        section_node = response.xpath('//*[@id="__next"]/main/article/div/div/div/div/div/div/section/node()')
        section_node = response.xpath('//*[@id="__next"]/main/article/div/div/div/div/div[1]/div/section/node()') if section_node is None else section_node
        img_urls = SolanaNewsSpider.__get_all_img_urls(response,str(title))

        if section_node is not None:
            content = SolanaNewsSpider.__content_cleaning_and_rebuilding(section_node)
        else:
            content = "<p>No content</p>"

        yield {
            'url': article_url,
            'platform': self.name,
            'date': article_date,
            'title': title,
            'content': content,
            'language': 'en',
            'images': img_urls,
        }

    @staticmethod
    def __content_cleaning_and_rebuilding(section_node):
        section_contents = section_node.getall()
        clean_sections = list()
        for content in section_contents:
            if content != '':
                clean_sections.append(content)
        return markdownify(''.join(clean_sections), heading_style="ATX")

    @staticmethod
    def __get_news_link_elements(response) -> List[scrapy.selector.unified.SelectorList]:
        count = 0
        while True:
            count += 1
            element: SelectorList = response.xpath(f'//*[@id="__next"]/main/div[3]/section/div/a[{count}]')
            if element:
                yield element
            else:
                return

    @staticmethod    
    def __get_all_img_urls(response, title):

        img_urls = response.xpath(f'//img[@alt="{title}"]/@src').getall()

        img_urls = [response.urljoin(url) for url in img_urls]

        if not img_urls:
            img_urls = []

        return img_urls
