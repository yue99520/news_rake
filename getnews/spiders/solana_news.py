from datetime import datetime, timezone
from typing import List

import lxml_html_clean as clean
import scrapy
from bs4 import BeautifulSoup
from scrapy.selector import SelectorList

SOLANA_FQDN = "solana.com"


class SolanaNewsSpider(scrapy.Spider):
    name = "solana_news"
    allowed_domains = [SOLANA_FQDN]
    start_urls = [f"https://{SOLANA_FQDN}/news"]

    # cleaner
    SAFE_ATTRS = {'src', 'alt', 'href', 'title', 'width', 'height'}
    KILL_TAGS = ['object', 'iframe']
    cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=SAFE_ATTRS, kill_tags=KILL_TAGS)

    def parse(self, response, **kwargs):
        for element in self.__get_news_link_elements(response):
            article_url = element.xpath('@href').get()
            yield scrapy.Request(f"https://{SOLANA_FQDN}{article_url}", callback=self.__parse_article, meta={'url': article_url})

    @staticmethod
    def __parse_article(response):
        article_url = response.meta['url']
        article_date = response.xpath('/html/head/meta[11]/@content').get()
        title = response.xpath('//*[@id="__next"]/main/div[2]/section/div/div/div[1]/h1/text()').get()
        section_node = response.xpath('//*[@id="__next"]/main/article/div/div/div/div/div/div/section/node()')
        section_node = response.xpath('//*[@id="__next"]/main/article/div/div/div/div/div[1]/div/section/node()') if section_node is None else section_node

        if section_node is not None:
            # TODO: define data schema with scrapy itme? Ernie 2024-07-21
            content = SolanaNewsSpider.__content_cleaning_and_rebuilding(section_node)
            item = {
                'url': article_url,
                'date': article_date,
                'title': title,
                'content': content
            }
        else:
            item = {
                'url': article_url,
                'date': article_date,
                'title': title,
                'content': "<p>No content</p>"
            }
        yield item

    @staticmethod
    def __content_cleaning_and_rebuilding(section_node):
        section_contents = section_node.getall()
        clean_sections = list()
        for content in section_contents:
            content = SolanaNewsSpider.__remove_invalid_tags(content)
            content = SolanaNewsSpider.__convert_weird_chars(content) if content != '' else ''
            content = SolanaNewsSpider.cleaner.clean_html(content) if content != '' else ''
            if content != '':
                clean_sections.append(content)
        return '<div>' + ''.join(clean_sections) + '</div>'

    @staticmethod
    def __convert_date_to_iso(date_str):
        # 定義日期字符串的格式
        date_format = "%d %B %Y"
        # 解析日期字符串
        date_obj = datetime.strptime(date_str, date_format)
        date_obj.astimezone(timezone.utc)
        iso_date_str = date_obj.isoformat()
        return iso_date_str

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
    def __remove_invalid_tags(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for section in soup.find_all('section'):
            section.decompose()
        for style in soup.find_all('style'):
            style.decompose()
        return str(soup)

    @staticmethod
    def __convert_weird_chars(html_content):
        html_content = html_content.replace('“', '"')
        html_content = html_content.replace('”', '"')
        html_content = html_content.replace('‘', "'")
        html_content = html_content.replace('’', "'")
        html_content = html_content.replace('–', "-")
        return html_content
