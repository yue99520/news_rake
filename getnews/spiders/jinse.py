import scrapy
import json

class JinseSpider(scrapy.Spider):
    name = "jinse"
    allowed_domains = ["api.jinse.com"]
    
    def __init__(self, limit=2, *args, **kwargs):
        super(JinseSpider, self).__init__(*args, **kwargs)
        self.limit = limit
        self.start_urls = [f"https://api.jinse.com/v4/live/list?limit={self.limit}&reading=false&flag=up"]

    def parse(self, response):
        data = json.loads(response.text)
        news_list = data.get('list', [])

        for news in news_list:
            date = news.get('date')
            lives = news.get('lives', [])
            
            for live in lives:
                article_url = live.get('link')
                article_date = date
                title = live.get('content')

                yield {
                    'url': article_url,
                    'platform': 'Jinse',
                    'date': article_date,
                    'title': title,
                }