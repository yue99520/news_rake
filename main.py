import os

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import getnews.spiders as sp
from getnews.storage import CMSClient

load_dotenv()


def run_spider():
    cms_client = CMSClient(
        graphql_endpoint="https://cms.gen3.network/api/graphql",
        identity=os.getenv('CMS_IDENTITY'),
        secret=os.getenv('CMS_PASSWORD')
    )
    if not cms_client.login():
        raise Exception("CMS Login failed")

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    # process the crawlers
    # process.crawl(sp.CoindeskSpider, cms_client)
    # process.crawl(sp.DecryptSpider, cms_client)
    # process.crawl(sp.FollowinSpider, cms_client)
    # process.crawl(sp.ForesightSpider, cms_client)
    # only get one article?
    # process.crawl(sp.JinseSpider, cms_client)
    # weird not work in here
    # process.crawl(sp.SolanaMediumSpider, cms_client)
    # process.crawl(sp.SolanaNewsSpider, cms_client)
    # no content
    # process.crawl(sp.TheBlockSpider, cms_client)
    # no content
    process.crawl(sp.ZombitSpider, cms_client)

    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    run_spider()
