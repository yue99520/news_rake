import scrapy
import feedparser
import re
from markdownify import markdownify

from getnews.storage import DecryptStorageHelper
from getnews.utils import TimeUtils

SOLANA_FQDN = "decrypt.co"


class DecryptSpider(scrapy.Spider):
    name = "decrypt"
    allowed_domains = ["decrypt.co"]
    start_urls = f"https://{SOLANA_FQDN}/feed"

    def __init__(self, cms_client, *args, **kwargs):
        super(DecryptSpider, self).__init__(*args, **kwargs)
        self.storage_helper = DecryptStorageHelper(cms_client, self.name)

    def start_requests(self):
            yield scrapy.Request(self.start_urls, callback=self.parse)
            
    def parse(self, response, **kwargs):
        rss = feedparser.parse(response.body)

        for entry in rss.entries:

            title = entry.get('title')
            date = entry.get('published')
            url = entry.get('link')
            print('url',url)
            if url and self.is_valid_url(url) and not self.storage_helper.does_exist(url=url):
                print('valid',url)
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.parse_news, meta={'lastmod': date, 'title': title})
    
    @staticmethod
    def is_valid_url(url):
        # Check if URL follows the pattern decrypt.co/[numbers]
        pattern = r"https://decrypt.co/\d+(/.*)?"
        return re.match(pattern, url) is not None
    
    def parse_news(self, response):
        article_url = response.url
        article_date = response.meta['lastmod']
        iso_article_date = TimeUtils.convert_datetime_to_iso8601(article_date, "%a, %d %b %Y %H:%M:%S %z")
        title = response.meta['title']
        paragraphs = response.xpath('//*[@id="__next"]/div/div[1]/div/main/div[2]/div/div/div[2]/div/div/div/div[1]/div/div').getall()
        content = self.__content_cleaning_and_rebuilding(paragraphs)
        image_urls = DecryptSpider.__get_all_img_urls(response)

        yield {
            'url': article_url,
            'platform': self.name,
            'date': iso_article_date,
            'title': title,
            'content': content,
            'language': 'en',
            'images': image_urls
        }

    @staticmethod
    def __content_cleaning_and_rebuilding(paragraphs):
        clean_paragraphs = []
        for paragraph in paragraphs:
            paragraph = markdownify(paragraph, heading_style="ATX")
            if paragraph.strip():
                clean_paragraphs.append(paragraph)
        return '\n\n'.join(clean_paragraphs)
    
    @staticmethod
    def __get_all_img_urls(response):
        img_urls = []
        xpath_path = '/html/body/div[1]/div/div[1]/div/main/div[2]/div/div/div[2]'
        
        img_elements = response.xpath(f'{xpath_path}//img')
        for img in img_elements:

            img_url = img.xpath('@src').get()

            if not img_url:
                img_url = img.xpath('@srcset').get()

            if img_url:
                img_url = response.urljoin(img_url)
                img_urls.append(img_url)

        if not img_urls:
            img_urls = []

        return img_urls
    

