import random
from datetime import datetime
from typing import List, Dict

import scrapy
from scrapy_splash import request
from markdownify import markdownify

from getnews.storage import TheBlockStorageHelper

THEBLOCK_FQDN = "www.theblock.co"


class TheBlockSpider(scrapy.Spider):
    name = "theblock"
    allowed_domains = ["www.theblock.co", "localhost", "splash-agent.local", "splash-agent.2local"]

    def __init__(self, cms_client, *args, **kwargs):
        super(TheBlockSpider, self).__init__(*args, **kwargs)
        self.storage_helper = TheBlockStorageHelper(cms_client, self.name)

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super(TheBlockSpider, self).__init__(*args, **kwargs)
        self.spider_context = self.storage_helper.get_spider_context_or_none(self.name)
        self.extra_info = self.spider_context['extra_info'] if self.spider_context else None
        self.extra_info = self.extra_info if self._initialized_extra_info(self.extra_info) else {
            'sitemap_index': 16,
            'last_article_modified': "2024-08-15 13:55 -04:00",
        }
        self.logger.info(f"theblock extra_info: {self.extra_info}")

    @staticmethod
    def _initialized_extra_info(extra_info):
        return extra_info is not None and len(extra_info.keys()) > 0

    def start_requests(self):
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://example.com'
        }

        sitemap_index = self.extra_info['sitemap_index']
        last_article_modified = self.extra_info['last_article_modified']
        extra_info_list = [
            {'sitemap_index': sitemap_index, 'last_article_modified': last_article_modified},
            {'sitemap_index': sitemap_index + 1, 'last_article_modified': None},
        ]
        for extra_info in extra_info_list:
            yield request.SplashRequest(f"https://www.theblock.co/sitemap_tbco_post_type_post_{extra_info['sitemap_index']}.xml",
                                        headers=headers,
                                        callback=self.parse,
                                        args={'wait': 2},
                                        meta={'extra_info': extra_info})

    def parse(self, response, **kwargs):
        if response.status == 404:
            return
        for article_info in self._get_news_link_elements(response):
            yield request.SplashRequest(article_info['article_url'],
                                        callback=self.__parse_article,
                                        args={'wait': 1},
                                        meta=article_info)

    def _get_news_link_elements(self, response) -> List[dict]:
        count = 0
        while True:
            count += 1
            article_url = response.xpath(f'/html/body/div/table/tbody/tr[{count}]/td[1]/a/@href').get()
            article_date = response.xpath(f"/html/body/div/table/tbody/tr[{count}]/td[5]/text()").get()
            extra_info = response.meta['extra_info']
            if article_url is not None and article_date is not None:
                if not self._article_exists(article_url, article_date, extra_info):
                    extra_info['last_article_modified'] = article_date
                    yield {
                        "article_url": article_url,
                        "article_date": article_date,
                        "extra_info": extra_info,
                    }
                else:
                    continue
            else:
                return

    def _article_exists(self, article_url, article_date, extra_info):
        if extra_info['last_article_modified'] is None:
            return self.storage_helper.does_exist(url=article_url)
        article_date_inst = datetime.fromisoformat(article_date)
        last_article_date_inst = datetime.fromisoformat(extra_info['last_article_modified'])
        if article_date_inst <= last_article_date_inst:
            return True
        else:
            extra_info['last_article_modified'] = article_date
            return False

    @staticmethod
    def __parse_article(response):
        extra_info = response.meta['extra_info']
        article_url = response.meta['article_url']
        article_date = response.meta['article_date']
        article_title = response.xpath('//meta[@property="og:title"]/@content').get()
        article_node = response.xpath('//*[@id="contentRoot"]/div/section/div[2]/article')
        contents = list()
        image = article_node.xpath('.//div[contains(@class, "articleFeatureImage")]').get()
        if image:
            contents.append(image)
        contents.extend(article_node.xpath('//*[@id="articleContent"]').getall())
        article_content = '<div>' + ''.join(contents) + '</div>'

        article_content = markdownify(article_content, heading_style="ATX")
        img_urls = TheBlockSpider.__get_all_img_urls(response)
        
        yield {
            'url': article_url,
            'platform': THEBLOCK_FQDN,
            'date': article_date,
            'title': article_title,
            'content': article_content,
            'language': 'en',
            'images': img_urls
        }
        
    @staticmethod
    def __get_all_img_urls(response):
        img_url = response.xpath('//div[contains(@class, "articleFeatureImage type:primaryImage")]/img/@src').get()

        if img_url:
            img_url = response.urljoin(img_url)
        else:
            img_url = []

        return img_url
