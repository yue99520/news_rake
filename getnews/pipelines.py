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
        if spider.name not in ['solana_news', 'solana_medium', 'theblock', 'followin']:
            return item
        directory = f'output/{spider.name}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + '/' + item['url'].split('/')[-1] + '.html', 'w') as f:
            f.write("<html>")
            f.write("<head>")
            f.write("<meta charset=\"UTF-8\">")
            f.write("<title>" + item['title'] + "</title>")
            f.write("</head>")
            f.write("<body>")
            f.write("<h2>" + item['title'] + "</h2>")
            f.write("<p>" + item['date'] + "</p>")
            f.write(item['content'])
            f.write("</body></html>")
        return item
