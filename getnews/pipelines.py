import os
import sys
import pika
import json
from itemadapter import ItemAdapter

class GetnewsPipeline:
    def process_item(self, item, spider):
        return item

class DebugOutputPipeline:

    def __init__(self):
        self.is_production = False # os.getenv('ENV', 'development') == 'production'

        try:
            print("Connecting to RabbitMQ...", os.getenv('RABBITMQ_HOST', 'localhost'))
            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
            rabbitmq_user = os.getenv('RABBITMQ_USER', 'user')
            rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'password')

            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            connection_params = pika.ConnectionParameters(
                host=rabbitmq_host,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.queue_name = 'scrapy_queue'

            self.channel.queue_declare(queue=self.queue_name, durable=True)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}", file=sys.stderr)
            sys.exit(1)  # fail the spider

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
        
        message = {
            'url': item['url'],
            'title': item['title'],
            'date': item['date'],
            'content': item['content'],
            'platform': item['platform']
        }
        # help me send json type item
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2, 
            )
        )

        if not self.is_production:
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

    def close_spider(self, spider):
        self.connection.close()
