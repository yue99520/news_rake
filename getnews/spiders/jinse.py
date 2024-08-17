import scrapy
import json
from markdownify import markdownify

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
                
                article_id = live.get('id')
                article_date = date
                raw_content = live.get('content')
                
                title, content = self.extract_title_and_content(raw_content)
                content = markdownify(content, heading_style="ATX"),
                yield {
                    'url': f'https://www.jinse.cn/lives/{article_id}.html',
                    'platform': 'Jinse',
                    'date': article_date,
                    'title': title,
                    'content': content,
                    'language': 'cn',   
                }
                
    def extract_title_and_content(self,raw_title):
        # title 是以【】包住的部分，content 是剩餘的部分
        title_start = raw_title.find("【")
        title_end = raw_title.find("】")

        # 提取 title
        if title_start != -1 and title_end != -1:
            title = raw_title[title_start + 1:title_end]
        else:
            title = raw_title  # 如果找不到【】就把整段當作 title
        
        # 提取 content
        content = raw_title[title_end + 1:].strip()  # 去除 title 之後的部分作為 content

        return title, content