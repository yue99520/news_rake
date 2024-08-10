import random
from typing import List, Dict

import scrapy
from scrapy_splash import request

THEBLOCK_FQDN = "www.theblock.co"


class TheBlockSpider(scrapy.Spider):
    name = "theblock"
    allowed_domains = ["www.theblock.co", "splash-agent.local", "splash-agent.2local"]
    start_urls = ["https://www.theblock.co/sitemap_tbco_news.xml"]

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    }

    def start_requests(self):
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://example.com'
        }

        for url in self.start_urls:
            yield request.SplashRequest(url, headers=headers, callback=self.parse, args={'wait': 2})

    def parse(self, response, **kwargs):
        print(response)
        for article_info in self.__get_news_link_elements(response):
            yield request.SplashRequest(article_info['article_url'],
                                        callback=self.__parse_article,
                                        args={'wait': 1},
                                        meta={
                                            "article_url": article_info['article_url'],
                                            "article_date": article_info['article_date'],
                                            "article_title": article_info['article_title']
                                        })

    @staticmethod
    def __get_news_link_elements(response) -> List[Dict]:
        count = 0
        while True:
            count += 1
            article_url = response.xpath(f'/html/body/div/table/tbody/tr[{count}]/td[1]/a/@href').get()
            if article_url:
                article_date = response.xpath(
                    f'/html/body/div/table/tbody/tr[{count}]/td[1]/p/text()[3]').get().replace(' Date: ', '').strip()
                article_title = response.xpath(
                    f'/html/body/div/table/tbody/tr[{count}]/td[1]/p/text()[4]').get().replace(' Title: ', '').strip()
                yield {
                    "article_url": article_url,
                    "article_date": article_date,
                    "article_title": article_title
                }
            else:
                return

    @staticmethod
    def __parse_article(response):
        article_url = response.meta['article_url']
        article_date = response.meta['article_date']
        article_title = response.meta['article_title']
        article_node = response.xpath('//*[@id="contentRoot"]/div/section/div[2]/article')
        contents = list()
        image = article_node.xpath('.//div[contains(@class, "articleFeatureImage")]').get()
        if image:
            contents.append(image)
        contents.extend(article_node.xpath('.//div[@id="articleContent"]/span/p').getall())
        article_content = '<div>' + ''.join(contents) + '</div>'
        yield {
            'url': article_url,
            'platform': THEBLOCK_FQDN,
            'date': article_date,
            'title': article_title,
            'content': article_content,
        }
