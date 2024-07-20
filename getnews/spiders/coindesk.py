import scrapy


class CoindeskSpider(scrapy.Spider):
    name = "coindesk"
    allowed_domains = ["www.coindesk.com"]
    start_urls = ["https://www.coindesk.com/"]

    def parse(self, response):
        pass
