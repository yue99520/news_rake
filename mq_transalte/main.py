import asyncio
import aio_pika
from aio_pika import Message
from aiohttp import ClientSession
import json
import os
import requests

# RabbitMQ 
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
QUEUE_NAME = 'scrapy_queue'

# Notion API 
NOTION_API_URL = "https://api.notion.com/v1/pages/"
NOTION_API_KEY = os.getenv('NOTION_API_KEY')  
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

async def translate_text(text: str) -> str:
   return text # will implement this later

def send_to_notion(platform_name, news_topic_cn, news_topic_eng, url, content_cn, content_eng, news_pic, date, origin_language):
    payload = json.dumps({
        "parent": {
            "database_id": NOTION_DATABASE_ID
        },
        "properties": {
            "Platform name": {
                "title": [
                    {
                        "text": {
                            "content": platform_name
                        }
                    }
                ]
            },
            "News topic CN": {
                "rich_text": [
                    {
                        "type": "text",
                        "plain_text": news_topic_cn
                    }
                ]
            },
            "News topic ENG": {
                "rich_text": [
                    {
                        "type": "text",
                        "plain_text": news_topic_eng
                    }
                ]
            },
            "URL": {
                "url": url
            },
            "Content CN": {
                "rich_text": [
                    {
                        "type": "text",
                        "plain_text": content_cn
                    }
                ]
            },
            "Content ENG": {
                "rich_text": [
                    {
                        "type": "text",
                        "plain_text": content_eng
                    }
                ]
            },
            "News pic": {
                "files": [
                    {
                        "name": news_pic["ImageName"],
                        "external": {
                            "url": news_pic["ImageURL"]
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date,
                    "end": None
                }
            },
            "Language": {
                "multi_select": [
                    {
                        "name": origin_language
                    }
                ]
            }
        }
    })

    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-05-13'
    }

    response = requests.post(NOTION_API_URL, headers=headers, data=payload)
    print(response.text)

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            body = message.body.decode('utf-8')
            item = json.loads(body)
            text = item.get('content', '')

            translated_text = await translate_text(text)
            
            platform_name = item.get('platform', '')
            news_topic_cn = item.get('title', '')
            news_topic_eng = 'Translated Title'  
            url = item.get('url', '')
            content_cn = item.get('content', '')
            content_eng = translated_text
            news_pic = {"ImageName": "example.jpg", "ImageURL": "http://example.com/image.jpg"}  
            date = item.get('date', '')
            origin_language = 'Chinese'  

            send_to_notion(platform_name, news_topic_cn, news_topic_eng, url, content_cn, content_eng, news_pic, date, origin_language)

        except Exception as e:
            print(f"Failed to process message: {e}")

async def main():
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
    )

    async with connection:
        async with connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(body=b''),
                routing_key=QUEUE_NAME
            )

            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            async for message in queue:
                await on_message(message)

if __name__ == '__main__':
    asyncio.run(main())
