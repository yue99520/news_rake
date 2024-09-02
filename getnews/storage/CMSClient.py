import json

import os
import requests


class CMSClient:
    def __init__(self, graphql_endpoint, identity, secret):
        self.graphql_endpoint = graphql_endpoint
        self.identity = identity
        self.secret = secret
        self.session = requests.Session()

    def login(self):
        login_mutation = """
        mutation ($identity: String!, $secret: String!) {
          authenticate: authenticateUserWithPassword(email: $identity, password: $secret) {
            ... on UserAuthenticationWithPasswordSuccess {
              item {
                id
                __typename
              }
              __typename
            }
            ... on UserAuthenticationWithPasswordFailure {
              message
              __typename
            }
            __typename
          }
        }
        """
        login_variables = {
            "identity": self.identity,
            "secret": self.secret
        }
        response = self.session.post(
            self.graphql_endpoint,
            json={"query": login_mutation, "variables": login_variables}
        )
        data = response.json()
        auth_data = data.get("data", {}).get("authenticate", {})

        if auth_data.get("__typename") == "UserAuthenticationWithPasswordSuccess":
            print("Login successful!")
        else:
            print("Login failed!")
            print(response.text)
            return False
        return True

    def list_crawlers_by_page(self, take=10, offset=0):
        list_crawlers_query = """
            query ListCrawlers($take: Int!, $skip: Int!) {
                crawlers: crawlers(
                    take: $take,  # 每頁返回的條目數
                    skip: $skip    # 跳過的條目數（即从第 skip+1 个条目开始返回）
                ) {
                    id
                    CID
                    URL
                    date
                    platformName
                    newsTopicCN
                    newsTopicEN
                    contentCN
                    contentEN
                    newsPic
                }
            }
        """
        response_data = requests.post(
            self.graphql_endpoint,
            json={
                "query": list_crawlers_query,
                "variables": {
                    "take": take,
                    "skip": offset
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["crawlers"]
        print(response_data['errors'][0]['message'])
        return []

    def get_crawler_or_none(self, url):
        get_crawler_query = """
        query GetCrawler($url: String!) {
            crawler: crawler(
                where: { URL: $url }
            ) {
                id
                URL
                date
                platformName
                newsTopicCN
                newsTopicEN
                contentCN
                contentEN
                newsPic
                spider {
                    spiderName
                    extraInfo
                    updatedAt
                }
            }
        }
        """
        response_data = requests.post(
            self.graphql_endpoint,
            json={
                "query": get_crawler_query,
                "variables": {
                    "url": url
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["crawler"]
        return None

    def create_crawler(self, crawler, spider):
        create_crawler_mutation = """
        mutation ($crawler: CrawlerCreateInput!, $spider: SpiderUpdateInput!, $spiderName: String!) {
            crawler: createCrawler(data: $crawler) {
                CID
                URL
                date
                language
                platformName
                newsTopicCN
                newsTopicEN
                contentCN
                contentEN
                newsPic
                spider {
                    spiderName
                    extraInfo
                    updatedAt
                }
            }
            spider: updateSpider(
                where: { spiderName: $spiderName }
                data: $spider
            ) {
                spiderName
                extraInfo
                updatedAt
            }
        }
        """
        response_data = self.session.post(
            self.graphql_endpoint,
            json={
                "query": create_crawler_mutation,
                "variables": {
                    "crawler": crawler,
                    "spider": spider,
                    "spiderName": spider["spiderName"]
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["crawler"]
        raise Exception(response_data['errors'][0]['message'])

    def delete_crawler(self, url):
        delete_crawler_mutation = """
        mutation DeleteCrawler($url: String!) {
          crawler: deleteCrawler(where: { URL: $url }) {
            CID
          }
        }
        """
        response_data = self.session.post(
            self.graphql_endpoint,
            json={
                "query": delete_crawler_mutation,
                "variables": {
                    "url": url
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["crawler"]
        return None

    def get_spider_or_none(self, spider_name):
        get_spider_context_query = """
        query GetSpiderContext($spiderName: String!) {
            spider: spider(
                where: { spiderName: $spiderName }
            ) {
                spiderName
                latestArticle {
                    CID
                }
                extraInfo
                updatedAt
            }
        }
        """
        response_data = requests.post(
            self.graphql_endpoint,
            json={
                "query": get_spider_context_query,
                "variables": {
                    "spiderName": spider_name
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["spider"]
        return None

    def create_spider(self, data):
        create_spider_context_mutation = """
            mutation ($data: SpiderCreateInput!) {
                spider: createSpider(data: $data) {
                    spiderName
                    extraInfo
                    updatedAt
                }
            }
        """
        response_data = self.session.post(
            self.graphql_endpoint,
            json={
                "query": create_spider_context_mutation,
                "variables": {
                    "data": data
                }
            }
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["spider"]
        raise Exception(response_data['errors'][0]['message'])


if __name__ == '__main__':
    cms_client = CMSClient(
        graphql_endpoint="https://cms.gen3.network/api/graphql",
        identity=os.getenv("CMS_IDENTITY"),
        secret=os.getenv("CMS_PASSWORD")
    )
    if cms_client.login():
        crawler_data = cms_client.get_spider_or_none("solana_news")
        print(crawler_data)
