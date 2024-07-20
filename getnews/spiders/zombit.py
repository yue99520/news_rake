import scrapy


class ZombitSpider(scrapy.Spider):
    name = "zombit"
    allowed_domains = ["zombit.info"]
    start_urls = ["https://zombit.info/"]

    def parse(self, response):
        pass
