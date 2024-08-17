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
    processed_item = await pipeline.process_item(item, None)

    zh = processed_item["zh_tw"]
    assert zh['title'] == "翻譯後的標題"
    assert zh['content'] == "翻譯後的內容"
    assert zh['language'] == "zh_tw"

    en = processed_item["en"]
    assert en['title'] == "Title"
    assert en['content'] == "Content"
    assert en['language'] == "en"

    assert processed_item["origin_language"] == "en"


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
    processed_item = await pipeline.process_item(item, None)

    zh = processed_item["zh_tw"]
    assert zh['title'] == "標題"
    assert zh['content'] == "內容"
    assert zh['language'] == "zh_tw"

    en = processed_item["en"]
    assert en['title'] == "Translated Title"
    assert en['content'] == "Translated Content"
    assert en['language'] == "en"

    assert processed_item["origin_language"] == "zh_tw"
