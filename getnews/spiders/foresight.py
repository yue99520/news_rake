import scrapy
from scrapy_splash import SplashRequest


class ForesightSpider(scrapy.Spider):
    name = "foresight"
    allowed_domains = ["foresightnews.pro"]
    start_urls = ["https://foresightnews.pro/news"]
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 5})    

    def parse(self, response):
        # 解析日期
        date_element = response.xpath('/html/body/div[1]/div/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/span/span/div')
        date_month = date_element.xpath('./div[@class="collapse-title-month"]/text()').get()
        date_year = date_element.xpath('./div[@class="collapse-title-right"]/div[1]/text()').get()
        article_date = f"{date_year} {date_month}"

        # 解析新聞
        articles = response.xpath('/html/body/div[1]/div/div/div[1]/div[1]/div/div[1]/div[2]/div[1]/ul/li')
        for article in articles:
            title = article.xpath('.//a[@class="news_body_title"]/text()').get()
            article_url = response.urljoin(article.xpath('.//a[@class="news_body_title"]/@href').get())
            content = article.xpath('.//div[@class="news_body_content"]/span/text()').get()

            yield {
                'url': article_url,
                'platform': 'foresightnews',
                'date': article_date,
                'title': title,
                'content': content
            }