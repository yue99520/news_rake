import asyncio
import aio_pika
from aio_pika import Message
from aiohttp import ClientSession
import json
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
# RabbitMQ 
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password')
QUEUE_NAME = 'scrapy_queue'

# Notion API 
NOTION_API_URL = "https://api.notion.com/v1/pages/"
NOTION_API_KEY = os.getenv('NOTION_API_KEY')  
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Generative AI
MODEL_API_KEY = os.getenv('MODEL_API_KEY')
genai.configure(api_key=MODEL_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def translate_text_en(text: str) -> str:
    response = model.generate_content(f"Translate this text to English:/n/n {text}")
    return response.text

async def translate_text_zh(text: str) -> str:
    response = model.generate_content(f"幫我翻譯成繁體中文:/n/n {text}")
    return response.text

async def to_normal_text(text: str) -> str:
    response = model.generate_content(f"幫我轉成正常的文字 去掉html tag:/n/n {text}")
    return response.text

def send_to_notion(platform_name, news_topic_cn, news_topic_eng, url, content_cn, content_eng, news_pic, date, origin_language):
    print(platform_name, news_topic_cn, news_topic_eng, url, content_cn, content_eng, news_pic, date, origin_language)
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
                        "text": {
                            "content": news_topic_cn
                        }
                    }
                ]
            },
            "News topic ENG": {
                "rich_text": [
                    {
                        "text": {
                            "content": news_topic_eng
                        }
                    }
                ]
            },
            "URL": {
                "url": url
            },
            "Content CN": {
                "rich_text": [
                    {
                        "text": {
                            "content": content_cn[0:1995]
                        }
                    }
                ]
            },
            "Content ENG": {
                "rich_text": [
                    {
                        "text": {
                            "content": content_eng[0:1995]
                        }
                    }
                ]
            },
            "News pic": {
                "files": [
                    {
                        "name": news_pic["ImageName"],
                        "external": {
                            "url": "https://example.com" # news_pic["ImageURL"]
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
                "select": 
                    {
                        "name": origin_language
                    }
                
            }
        }
    })

    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-05-13'
    }

    response = requests.post(NOTION_API_URL, headers=headers, data=payload)
    print('notion',response.text)

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            body = message.body.decode('utf-8')
            item = json.loads(body)
            text = item.get('content', '')

            translated_text = await translate_text_en(text)
            
            platform_name = item.get('platform', '')
            news_topic_cn = item.get('title', '')
            news_topic_eng = 'Translated Title'  
            url = item.get('url', '')
            content_cn = await to_normal_text(item.get('content', ''))
            content_eng = translated_text
            news_pic = {"ImageName": "example.jpg", "ImageURL": ""}  
            date = item.get('date', '')
            origin_language = 'CN'  

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
