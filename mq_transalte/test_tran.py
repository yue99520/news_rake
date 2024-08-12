import os
import asyncio
import google.generativeai as genai

MODEL_API_KEY = os.getenv('MODEL_API_KEY')
genai.configure(api_key=MODEL_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def translate_text_en(text: str) -> str:
    response = model.generate_content(f"Translate this text to English:/n/n {text}")
    return response

async def translate_text_zh(text: str) -> str:
    response = model.generate_content(f"幫我翻譯成繁體中文:/n/n {text}")
    return response

async def to_normal_text(text: str) -> str:
    response = model.generate_content(f"幫我轉成正常的文字:/n/n {text}")
    return response.text
async def main():
    text = "a quick brown fox jumps over the lazy dog"
    response = await translate_text_zh(text)
    print(response.text)
    en_response = await translate_text_en(response.text)
    print(en_response.text)

if __name__ == '__main__':
    asyncio.run(main())
