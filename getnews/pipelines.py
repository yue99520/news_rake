# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class GetnewsPipeline:

    def process_item(self, item, spider):
        return item


class DebugOutputPipeline:
    def process_item(self, item, spider):
        """
            item: dict
            item fields:
            - url (str, full url)
            - title (str)
            - date (str, iso8601)
            - content (str, include html tags)
            - platform (str)
        """
        if spider.name not in ['solana_news', 'solana_medium', 'theblock', 'followin', 'coindesk', 'foresight']:
            return item
        directory = f'output/{spider.name}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        url: str = item['url']
        if url.endswith("/"):
            url = url[:-1]
        with open(directory + '/' + url.split('/')[-1] + '.html', 'w') as f:
            f.write("<html>")
            f.write("<head>")
            f.write("<meta charset=\"UTF-8\">")
            f.write("<title>" + item['title'] + "</title>")
            f.write("</head>")
            f.write("<body>")
            f.write("<h2>" + item['title'] + "</h2>")
            if item['date'] is not None:
                f.write("<p>" + item['date'] + "</p>")
            if item['url'] is not None:
                f.write(f'<a href="{item["url"]}">' + item['url'] + '</a>')
            f.write(item['content'])
            f.write("</body></html>")
        return item
