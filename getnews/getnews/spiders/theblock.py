import scrapy


class TheblockSpider(scrapy.Spider):
    name = "theblock"
    allowed_domains = ["www.theblock.co"]
    start_urls = ["https://www.theblock.co/"]

    def parse(self, response):
        pass
