import scrapy


class CoingeckoSpider(scrapy.Spider):
    name = "coingecko"
    allowed_domains = ["www.coingecko.com"]
    start_urls = ["https://www.coingecko.com/en/news"]

    def parse(self, response):
        pass
