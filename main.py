from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import getnews.spiders as sp

def run_spider():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    # process the crawlers
    process.crawl(sp.CoindeskSpider)
    process.crawl(sp.DecryptSpider)
    process.crawl(sp.FollowinSpider)
    process.crawl(sp.ForesightSpider)
    process.crawl(sp.JinseSpider)
    process.crawl(sp.SolanaMediumSpider)
    process.crawl(sp.SolanaNewsSpider)
    process.crawl(sp.TheBlockSpider)
    process.crawl(sp.ZombitSpider)


    process.start()  # the script will block here until the crawling is finished

if __name__ == '__main__':
    
    run_spider()