import scrapy


class SolanaMediumSpider(scrapy.Spider):
    name = "solana_medium"
    allowed_domains = ["medium.com"]
    start_urls = ["https://medium.com/@solanafoundation"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)
    
    def parse(self, response):
        pass
