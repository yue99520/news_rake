import scrapy


class JinseSpider(scrapy.Spider):
    name = "jinse"
    allowed_domains = ["www.jinse.cn"]
    start_urls = ["https://www.jinse.cn/"]

    def parse(self, response):
        pass
