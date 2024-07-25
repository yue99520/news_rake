import scrapy
##需要使用selenium才能取得所有新聞的Link
solana_fqdn = "decrypt.co"
class DecryptSpider(scrapy.Spider):
    name = "decrypt"
    allowed_domains = ["decrypt.co"]
    start_urls = f"https://{solana_fqdn}/"

    def start_requests(self):
            yield scrapy.Request(self.start_urls, callback=self.parse)
            
    def parse(self, response):
        # 選擇所有新聞文章的元素
        articles = response.xpath('//div[@class="mt-2 md:mt-4 xl:flex xl:space-x-5"]/div')

        for article in articles:
            # 解析標題
            title = article.xpath('.//h3/a/text()').get() or article.xpath('.//h3/span/text()').get()
            # 解析日期
            date = article.xpath('.//time[1]/@datetime').get()
            # 解析鏈接
            link_url = article.xpath('.//h3/a/@href').get()
            if link_url:
                link_url = response.urljoin(link_url)

            yield {
                'title': title,
                'date': date,
                'link_url': link_url
            }
