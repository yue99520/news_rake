from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from playhouse.postgres_ext import PostgresqlExtDatabase

import getnews.spiders as sp
import getnews.storage as storage


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
    db = None
    try:
        db = storage.DBControl(PostgresqlExtDatabase(
            'gen3_crawler',
            user='user',
            password='password',
            host='localhost',
            port=5432
        ))
        db.connect()
        db.create_tables()
        run_spider()

    finally:
        if db is not None:
            db.close()
