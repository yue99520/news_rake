from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from playhouse.postgres_ext import PostgresqlExtDatabase

import getnews.spiders as sp
import getnews.storage as storage

import asyncio
from dotenv import load_dotenv
load_dotenv()

def run_spider():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    # process the crawlers
    # process.crawl(sp.CoindeskSpider)
    # process.crawl(sp.DecryptSpider)
    # process.crawl(sp.FollowinSpider)
    # process.crawl(sp.ForesightSpider)
    # only get one article?
    # process.crawl(sp.JinseSpider)
    # weird not work in here
    # process.crawl(sp.SolanaMediumSpider)
    # process.crawl(sp.SolanaNewsSpider)
    # no content
    # process.crawl(sp.TheBlockSpider)
    # no content
    # process.crawl(sp.ZombitSpider)

    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    run_spider()
