import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Generative AI
MODEL_API_KEY = os.getenv('MODEL_API_KEY')
genai.configure(api_key=MODEL_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class gemini_translate:
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