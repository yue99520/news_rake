import asyncio
import aio_pika
from aio_pika import Message
from aiohttp import ClientSession
import json
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password')
QUEUE_NAME = 'scrapy_queue'

async def translate_text(text: str) -> str:
    return text  # for now, we'll return the original text
    # api_key = os.getenv('CHATGPT_API_KEY')  # 假設你使用環境變數來儲存 API 密鑰
    # url = 'https://api.openai.com/v1/engines/text-davinci-003/completions'
    # headers = {
    #     'Authorization': f'Bearer {api_key}',
    #     'Content-Type': 'application/json'
    # }
    # payload = {
    #     'prompt': f'Translate the following text to English:\n\n{text}',
    #     'max_tokens': 60
    # }

    # async with ClientSession() as session:
    #     async with session.post(url, headers=headers, json=payload) as response:
    #         result = await response.json()
    #         return result.get('choices', [{}])[0].get('text', '').strip()

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            print("Received message", message.body)
            body = message.body.decode('utf-8')
            item = json.loads(body)
            text = item.get('content', '')

            # translate the text
            translated_text = await translate_text(text)
            print(f"Original content:\n{text}")
            print(f"Translated content:\n{translated_text}")

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
