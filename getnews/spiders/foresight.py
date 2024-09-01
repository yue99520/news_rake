import scrapy
from markdownify import markdownify
from scrapy_splash import SplashRequest

from getnews.storage import ForesightStorageHelper
from getnews.utils import TimeUtils


class ForesightSpider(scrapy.Spider):
    name = "foresight"
    allowed_domains = [
        "foresightnews.pro",
        "localhost",
        "splash-agent.henry",
    ]
    start_urls = ["https://foresightnews.pro/news"]

    def __init__(self, cms_client, *args, **kwargs):
        super(ForesightSpider, self).__init__(*args, **kwargs)
        self.storage_helper = ForesightStorageHelper(cms_client, self.name)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 5})    

    def parse(self, response, **kwargs):
        # 解析日期
        date_element = response.xpath('/html/body/div[1]/div/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/span/span/div')
        date_month_and_day: str = date_element.xpath('./div[@class="collapse-title-month"]/text()').get()
        date_year = date_element.xpath('./div[@class="collapse-title-right"]/div[1]/text()').get()
        article_date = f"{date_year}年{date_month_and_day}"
        article_iso_date = TimeUtils.convert_datetime_to_iso8601(article_date, "%Y年%m月%d日")

        # 解析新聞
        articles = response.xpath('/html/body/div[1]/div/div/div[1]/div[1]/div/div[1]/div[2]/div[1]/ul/li')

        for article in articles:

            title_node = article.xpath('.//a[contains(@class, "news_body_title")]')

            title = title_node.xpath('.//text()').get()
            article_url = response.urljoin(title_node.xpath('.//@href').get())

            content = article.xpath('.//div[@class="news_body_content"]/span/text()').get()
            content = markdownify(content, heading_style="ATX")
            image_urls = ForesightSpider.__get_all_img_urls(response)

            yield {
                'url': article_url,
                'platform': self.name,
                'date': article_iso_date,
                'title': title,
                'content': content,
                'language': 'zh_tw',
                'images': image_urls,
            }
    
    @staticmethod    
    def __get_all_img_urls(response):

        xpath_range = '/html/body/div[1]/div/div/div[1]/div[1]/div/div/div[1]/div[5]/preceding::img'

        image_urls = response.xpath(f'{xpath_range}/@src').getall()

        if not image_urls:
            image_urls = []

        return image_urls
