import scrapy
##使用requests 獲得403錯誤

class CoingeckoSpider(scrapy.Spider):
    name = "coingecko"  
    allowed_domains = ["www.coingecko.com"]
    start_urls = ["https://www.coingecko.com/en/news"]

    def parse(self, response):
        pass
