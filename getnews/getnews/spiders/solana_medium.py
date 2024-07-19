import scrapy


class SolanaMediumSpider(scrapy.Spider):
    name = "solana_medium"
    allowed_domains = ["medium.com"]
    start_urls = ["https://medium.com/@solanafoundation"]

    def parse(self, response):
        pass
