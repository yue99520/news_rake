from typing import Iterable
import scrapy

class ZombitSpider(scrapy.Spider):
    name = "zombit"
    allowed_domains = ["zombit.info"]
    start_urls = ["https://zombit.info/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # 選擇所有新聞文章的元素
        articles = response.xpath('//div[@class="post-item row mb-4"]')

        for article in articles:
            # 解析標題
            title = article.xpath('.//h3[@class="post-title max-two-lines"]/a/text()').get()
            # 解析日期
            date = article.xpath('.//div[@class="post-date"]/text()').get()
            # 解析鏈接
            link_url = article.xpath('.//h3[@class="post-title max-two-lines"]/a/@href').get()
            if link_url:
                link_url = response.urljoin(link_url)
            # 解析新聞來源
            source = article.xpath('.//a[@class="post-author"]/div[@class="name"]/text()').get()

            yield {
                'title': title,
                'date': date,
                'link_url': link_url,
                'source': source
            }
