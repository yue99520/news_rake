import json
from typing import List

import scrapy
from scrapy.selector import SelectorList
from scrapy_splash import SplashRequest
from markdownify import markdownify

from getnews.storage import SolanaMediumStorageHelper
from getnews.utils.clean_utils import CleanUtils
from getnews.utils.time_utils import TimeUtils

SOLANA_FQDN = "solanafoundation.medium.com"


class SolanaMediumSpider(scrapy.Spider):
    name = "solana_medium"
    allowed_domains = ["medium.com", "localhost","splash-agent.local", "splash-agent.2local"]
    start_urls = ["https://solanafoundation.medium.com"]
    storage_helper = SolanaMediumStorageHelper()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        for url in self.__get_article_link(response):
            if self.storage_helper.does_exist(url=url):
                continue
            yield SplashRequest(url, callback=self.__parse_article, endpoint='render.html', meta={
                'url': url,
                'splash': {
                    'images': 1,
                    'args': {'wait': 2}
                }
            })

    @staticmethod
    def __get_article_link(response) -> List[scrapy.selector.unified.SelectorList]:
        count = 0
        while True:
            count += 1
            url: SelectorList = response.xpath(
                f'//*[@id="root"]/div/div[2]/div[2]/div/main/div/div[2]/div/div/div[{count}]/div/div/article/div/div/div/div/div[1]/@data-href').get()
            if url:
                yield url
            else:
                return

    @staticmethod
    def __parse_article(response):
        article_meta_raw = response.xpath('//script[@type="application/ld+json"][1]/text()').get()
        article_meta = json.loads(article_meta_raw)
        article_date = TimeUtils.convert_datetime_to_iso8601(article_meta['datePublished'], "%Y-%m-%dT%H:%M:%S.%fZ")
        article_url = response.meta['url']
        title = response.xpath('//meta[@name="title"][1]/@content').get().split(' | ')[0]
        content = SolanaMediumSpider.__get_article_paragraph(response)
        content = CleanUtils.remove_tags(content, ['style', 'script'])
        content = CleanUtils.convert_weird_chars(content)
        content = CleanUtils.clean_attributes(content)
        content = markdownify(content, heading_style="ATX")

        yield {
            'url': article_url,
            'platform': SOLANA_FQDN,
            'date': article_date,
            'title': title,
            'content': content,
            'language': 'en',
            'images': [],
        }

    @staticmethod
    def __get_article_paragraph(response) -> str:
        paragraphs = response.xpath('//*[contains(@class, "pw-post-body-paragraph")]')
        paragraphs = [p.get() for p in paragraphs]
        return '<div>' + ''.join(paragraphs) + '</div>'
