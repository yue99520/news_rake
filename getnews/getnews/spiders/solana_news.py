import scrapy


class SolanaNewsSpider(scrapy.Spider):
    name = "solana_news"
    allowed_domains = ["solana.com"]
    start_urls = ["https://solana.com/news"]

    def parse(self, response):
        pass
