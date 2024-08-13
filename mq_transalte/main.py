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
    response = model.generate_content(f"Translate this text to English help me type setting, not only one block, but no html tag and eng :/n/n {text}")
    return response.text

async def translate_title_en(text: str) -> str:
    response = model.generate_content(f"Translate this title to English, no add anything:/n/n {text}")
    return response.text

async def translate_text_zh(text: str) -> str:
    response = model.generate_content(f"幫我翻譯成繁體中文:/n/n {text}")
    return response.text

async def translate_title_zh(text: str) -> str:
    response = model.generate_content(f"幫我翻譯成繁體中文，不要亂加:/n/n {text}")
    return response.text

async def to_normal_text(text: str) -> str:
    response = model.generate_content(f"幫我轉成正常的文字 去掉htmltag 但格式換行的br要留給我 但不要改動原本語言:/n/n {text}")
    return response.text

def get_platfome_lang(name: str) -> str:
    if name in ['solana_news', 'solana_medium', 'coindesk', 'decrypt']:
        return 'EN'
    else:
        return 'CN'

def platform_img(name: str) -> str:
    # use a dict to store the image url
    imgList = {
        'solana_medium': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Solana_logo.png',
        'solana_news': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Solana_logo.png',
        'coindesk': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTO20V5GgEjI_m10je_LbHnkBM_TaRm1-kE9A&s',
        'decrypt': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Solana_logo.png',
        'followin': 'https://play-lh.googleusercontent.com/GTpsvKFZZ0cv5_au5LciVcrEWEVe6_P1xUj47wz0QgwUuHF93ZvojTW1Uj19nJxIBq4',
        'foreseight': 'https://pbs.twimg.com/card_img/1821735526829060096/9WQCjdWx?format=jpg&name=large',       
    }
    return imgList.get(name, 'https://upload.wikimedia.org/wikipedia/en/b/b9/Solana_logo.png')
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
            platform_name = item.get('platform', '')

            if (get_platfome_lang(platform_name) == 'EN'):
                translated_text = await translate_text_zh(text)
                news_topic_eng = item.get('title', '')
                news_topic_cn = await translate_title_zh(news_topic_eng)
                url = item.get('url', '')
                content_cn = translated_text
                content_eng = await to_normal_text(item.get('content', ''))
                news_pic = {"ImageName": f"{platform_name}.jpg", "ImageURL": ""}  
                date = item.get('date', '')
                origin_language = get_platfome_lang(platform_name)

                send_to_notion(platform_name, news_topic_cn, news_topic_eng, url, content_cn, content_eng, news_pic, date, origin_language)

            else:
                translated_text = await translate_text_en(text)
                news_topic_cn = item.get('title', '')
                news_topic_eng = await translate_title_en(news_topic_cn)
                url = item.get('url', '')
                content_cn = await to_normal_text(item.get('content', ''))
                content_eng = translated_text
                news_pic = {"ImageName": f"{platform_name}.jpg", "ImageURL": ""}  
                date = item.get('date', '')
                origin_language = get_platfome_lang(platform_name) 

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
