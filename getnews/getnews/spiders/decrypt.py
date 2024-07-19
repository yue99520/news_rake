import scrapy


class DecryptSpider(scrapy.Spider):
    name = "decrypt"
    allowed_domains = ["decrypt.co"]
    start_urls = ["https://decrypt.co/"]

    def parse(self, response):
        pass
