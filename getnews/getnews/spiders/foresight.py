import scrapy


class ForesightSpider(scrapy.Spider):
    name = "foresight"
    allowed_domains = ["foresightnews.pro"]
    start_urls = ["https://foresightnews.pro/"]

    def parse(self, response):
        pass
