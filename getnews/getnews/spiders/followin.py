import scrapy


class FollowinSpider(scrapy.Spider):
    name = "followin"
    allowed_domains = ["followin.io"]
    start_urls = ["https://followin.io/zh-Hant"]

    def parse(self, response):
        pass
