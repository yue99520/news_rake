import asyncio
import os
import sys
from datetime import datetime
from scrapy.exceptions import DropItem
from .utils import GeminiTranslate


class ItemVerifyPipeline:
    def process_item(self, item, spider):
        try:
            assert 'url' in item, "url is required"
            assert 'title' in item, "title is required"

            assert 'date' in item, "date is required"
            assert item['date'] is not None, "date is required"
            assert datetime.fromisoformat(item['date']) is not None, "date is not a valid datetime"

            assert 'content' in item, "content is required"
            assert 'platform' in item, "platform is required"
            assert 'language' in item, "language is required"
            assert 'images' in item, "images is required"
            assert isinstance(item["images"], list), "images must be a list"
            if 'extra_info' in item and item['extra_info'] is not None:
                # then it means this item will cause the extra_info to be updated
                assert isinstance(item['extra_info'], dict), "extra_info must be a dict"
        except Exception as e:
            spider.logger.error(f"[{spider.name}] Invalid item format. [{type(e).__name__}: {e}]")
            raise DropItem("ItemVerifyPipeline")

        return item


class TranslatePipeline:

    def __init__(self):
        self.translator = GeminiTranslate

    async def process_item(self, item, spider):
        extra_info = item['extra_info'] if 'extra_info' in item else None
        if item['language'] == 'en':
            return {
                "en": item,
                "zh_tw": await self._to_zh_item(item),
                "origin_language": "en",
                "extra_info": extra_info
            }
        elif item['language'] == 'zh_tw':
            return {
                "en": await self._to_en_item(item),
                "zh_tw": item,
                "origin_language": "zh_tw",
                "extra_info": extra_info
            }
        else:
            return {
                "en": await self._to_en_item(item),
                "zh_tw": await self._to_zh_item(item),
                "origin_language": "zh_tw",
                "extra_info": extra_info
            }

    async def _to_zh_item(self, item):
        zh_item = dict(item)
        zh_item['language'] = 'zh_tw'
        zh_item['title'], zh_item['content'] = await asyncio.gather(
            self.translator.translate_title_zh(item['title']),
            self.translator.translate_text_zh(item['content']))
        return zh_item

    async def _to_en_item(self, item):
        en_item = dict(item)
        en_item['language'] = 'en'
        en_item['title'], en_item['content'] = await asyncio.gather(
            self.translator.translate_title_en(item['title']),
            self.translator.translate_text_en(item['content']))
        return en_item


class StoragePipeline:
    def process_item(self, item, spider):
        origin_language = item['origin_language']
        platform_name = item[origin_language]['platform']
        url = item[origin_language]['url']

        storage_article = {
            "platform_name": platform_name,
            "spider_name": spider.name,
            "url": item[origin_language]['url'],
            "date": item[origin_language]['date'],
            "news_pic": item[origin_language]["images"],
            "origin_language": item['origin_language'],
            "news_topic_cn": item['zh_tw']['title'],
            "news_topic_eng": item['en']['title'],
            "content_cn": item['zh_tw']['content'],
            "content_eng": item['en']['content'],
        }

        if not hasattr(spider, 'storage_helper'):
            raise Exception("Spider must have a storage_helper")

        article, created = spider.storage_helper.safe_create_article(spider.name, storage_article, extra_info=item['extra_info'])
        if created:
            spider.logger.info(
                f"Created article: url={url}, title=[zh_tw={article.news_topic_cn}, en={article.news_topic_eng}]")
        else:
            spider.logger.warning(
                f"Skipped article: url={url}, title=[zh_tw={article.news_topic_cn}, en={article.news_topic_eng}]")
        return None


class DebugOutputPipeline:

    def __init__(self):
        self.is_production = False  # os.getenv('ENV', 'development') == 'production'
        if self.is_production:
            pass

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

        # # help me send json type item
        # self.channel.basic_publish(
        #     exchange='',
        #     routing_key=self.queue_name,
        #     body=json.dumps(message),
        #     properties=pika.BasicProperties(
        #         delivery_mode=2, 
        #     )
        # )

        # for debugging purpose
        if not self.is_production:
            print(f"===DebugOutputPipeline: {spider.name}\n")
            print(f"Title: {item['title']}\n")
            print(f"Date: {item['date']}\n")
            print(f"URL: {item['url']}\n")
            print(f"Content: {item['content']}\n")

        return item

    def close_spider(self, spider):
        # self.connection.close()
        pass
