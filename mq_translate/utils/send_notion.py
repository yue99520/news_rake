import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
# Notion API 
NOTION_API_URL = "https://api.notion.com/v1/pages/"
NOTION_API_KEY = os.getenv('NOTION_API_KEY')  
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

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