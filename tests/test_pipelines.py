from unittest.mock import AsyncMock

import pytest

from getnews.pipelines import TranslatePipeline


@pytest.mark.asyncio
async def test_process_item_translate_to_zh():
    pipeline = TranslatePipeline()

    pipeline.translator.translate_title_zh = AsyncMock(return_value="翻譯後的標題")
    pipeline.translator.translate_text_zh = AsyncMock(return_value="翻譯後的內容")

    item = {
        "title": "Title",
        "content": "Content",
        "language": "en"
    }
    processed_items = await pipeline.process_item(item, None)
    assert len(processed_items) == 2

    zh = [item for item in processed_items if item['language'] == 'zh_tw']
    assert len(zh) == 1
    assert zh[0]['title'] == "翻譯後的標題"
    assert zh[0]['content'] == "翻譯後的內容"
    assert zh[0]['language'] == "zh_tw"

    en = [item for item in processed_items if item['language'] == 'en']
    assert len(en) == 1
    assert en[0]['title'] == "Title"
    assert en[0]['content'] == "Content"
    assert en[0]['language'] == "en"


@pytest.mark.asyncio
async def test_process_item_translate_to_en():
    pipeline = TranslatePipeline()

    pipeline.translator.translate_title_en = AsyncMock(return_value="Translated Title")
    pipeline.translator.translate_text_en = AsyncMock(return_value="Translated Content")

    item = {
        "title": "標題",
        "content": "內容",
        "language": "zh_tw"
    }
    processed_items = await pipeline.process_item(item, None)

    zh = [item for item in processed_items if item['language'] == 'zh_tw']
    assert len(zh) == 1
    assert zh[0]['title'] == "標題"
    assert zh[0]['content'] == "內容"
    assert zh[0]['language'] == "zh_tw"

    en = [item for item in processed_items if item['language'] == 'en']
    assert len(en) == 1
    assert en[0]['title'] == "Translated Title"
    assert en[0]['content'] == "Translated Content"
    assert en[0]['language'] == "en"
