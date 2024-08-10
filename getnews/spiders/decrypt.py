import scrapy
import feedparser

SOLANA_FQDN = "decrypt.co"
class DecryptSpider(scrapy.Spider):
    name = "decrypt"
    allowed_domains = ["decrypt.co"]
    start_urls = f"https://{SOLANA_FQDN}/feed"

    def start_requests(self):
            yield scrapy.Request(self.start_urls, callback=self.parse)
            
    def parse(self, response):
        rss = feedparser.parse(response.body)
        for entry in rss.entries:

            title = entry.get('title')
            date = entry.get('published')
            url = entry.get('link')
            if url:
                url = response.urljoin(url)

            yield {
                'url': url,
                'platform': SOLANA_FQDN,
                'date': date,
                'title': title,
            }
