import os
import random
import unittest
from asyncio import sleep

from dotenv import load_dotenv

from getnews.storage import CMSClient
from getnews.utils import GeminiTranslate

load_dotenv()


class TestCMSClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = CMSClient(
            graphql_endpoint="https://cms.gen3.network/api/graphql",
            identity=os.getenv('CMS_IDENTITY'),
            secret=os.getenv('CMS_PASSWORD')
        )
        assert self.client.login()

    async def test_list_crawlers_by_page(self):
        take = 10
        offset = 0
        while True:
            print("------------")
            print(f"take: {take}, offset: {offset}")
            crawlers = self.client.list_crawlers_by_page(take, offset)
            offset += 1
            if crawlers is None:
                break
            for crawler in crawlers:
                try:
                    response = await GeminiTranslate.compare_translation(crawler["contentCN"], crawler["contentEN"])
                    await sleep(random.randrange(1, 5) / 5)
                    if response is None:
                        print(f"CID: {crawler["CID"]}, result: None")
                        continue
                    if not response:
                        print(f"CID: {crawler["CID"]}, \n\n{crawler} \n\n{crawler}")
                except Exception as e:
                    print(f"CID: {crawler['CID']}, error: {e}")


