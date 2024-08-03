import itertools
from datetime import datetime
from zoneinfo import ZoneInfo

import scrapy
from scrapy_splash import request

FORESIGHT_FQDN = "foresightnews.pro"


class ForesightSpider(scrapy.Spider):
    name = "foresight"
    allowed_domains = [
        "foresightnews.pro",
        "splash-agent.local",
        "splash-agent.2local",
    ]
    start_urls = ["https://foresightnews.pro/news"]

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://example.com'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield request.SplashRequest(
                url,
                headers=ForesightSpider.headers,
                callback=self.parse,
                args={'wait': 5},
            )

    def parse(self, response, **kwargs):
        yield from self.__get_news(response)

    @staticmethod
    def __get_news(response):
        news_bodies = response.xpath(f'//div[@class="news-body"]')
        print(f"There are {str(len(news_bodies))} news bodies")
        for news_body in news_bodies:
            yield from ForesightSpider.__parse_news_body(news_body)

    @staticmethod
    def __parse_news_body(news_body):
        data = list()
        for counter in itertools.count(start=1, step=1):
            el_timeline_item = news_body.xpath(f'.//li[contains(@class, "el-timeline-item")][{counter}]')
            if not el_timeline_item:
                break
            news_content = el_timeline_item.xpath('.//div[@class="news_content"]')
            if not news_content:
                break
            time_str = el_timeline_item.xpath(
                './/div[contains(@class, "el-timeline-item__timestamp")]/text()').get().strip()
            news_content_data = ForesightSpider.__parse_news_content(news_content)
            data.append({
                'time_str': time_str,
                'news_content_data': news_content_data,
            })
        if len(data) == 0:
            return
        get_date_url = data[0]['news_content_data']['url']
        print(f"Get date url: {get_date_url}")
        yield request.SplashRequest(get_date_url,
                                    headers=ForesightSpider.headers,
                                    callback=ForesightSpider.__parse_news_time,
                                    args={'wait': 2},
                                    meta={'data': data})

    @staticmethod
    def __parse_news_content(news_content):
        title_node = news_content.xpath('.//a[contains(@class, "news_body_title")][1]')
        article_title = title_node.xpath('.//text()').get()
        article_url = f"https://{FORESIGHT_FQDN}{title_node.xpath('.//@href').get()}"
        article_text = news_content.xpath('.//div[contains(@class, "news_body_content")][1]/span/text()').get()
        article_content = f"<p>{article_text}</p>"
        return {
            'url': article_url,
            'platform': FORESIGHT_FQDN,
            'date': None,
            'title': article_title,
            'content': article_content,
        }

    @staticmethod
    def __parse_news_time(response):
        data = response.meta['data']
        raw = response.xpath('//div[contains(@class, "topic-time")]/text()').get()
        date_and_time = raw.split(" , ")
        date_str = date_and_time[0].strip(" ")
        print(f"Date str: {date_str}")
        local_tz = datetime.now().astimezone().tzinfo

        for item in data:
            news_content = item['news_content_data']
            news_content['date'] = datetime.strptime(f'{date_str}T{item["time_str"]}', "%Y-%m-%dT%H:%M").replace(
                tzinfo=local_tz).astimezone(ZoneInfo("UTC")).isoformat()
            yield news_content
