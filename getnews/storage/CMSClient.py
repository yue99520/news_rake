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

    def get_crawler_or_none(self, url):
        # TODO: change back to unique where statement
        get_crawler_query = """
        query GetCrawler($url: String!) {
            crawler(
                where: { URL: $url }
            ) {
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
        # get_crawler_query = """
        # query GetCrawler($url: StringFilter!) {
        #     crawlers(
        #         where: { URL: $url }
        #     ) {
        #         id: CID
        #         url
        #         date
        #         platform_Name
        #         newsTopicCN
        #         newsTopicEN
        #         contentCN
        #         contentEN
        #         newsPic
        #     }
        # }
        # """
        response_data = requests.post(
            self.graphql_endpoint,
            json={
                "query": get_crawler_query,
                "variables": {
                    "url": url
                }
            }
        ).json()

        print(response_data)
        if "errors" not in response_data:
            return response_data["data"]["crawler"]
        return None

    def create_crawler(self, data):
        create_crawler_mutation = """
        mutation ($data: CrawlerCreateInput!) {
            crawler: createCrawler(data: $data) {
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
        response_data = self.session.post(
            self.graphql_endpoint,
            json={"query": create_crawler_mutation, "variables": {"data": data}}
        ).json()
        if "errors" not in response_data:
            return response_data["data"]["crawler"]
        return None

    def delete_crawler(self, cid):
        delete_crawler_mutation = """
        mutation DeleteCrawler($cid: Int!) {
          deleteCrawler(where: { CID: $cid }) {
            CID
          }
        }
        """
        self.session.post(
            self.graphql_endpoint,
            json={
                "query": delete_crawler_mutation,
                "variables": {
                    "cid": cid
                }
            }
        )

    def get_spider_context_or_none(self, spider_name):
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

    def create_spider_context(self, data):
        create_spider_context_mutation = """
            mutation CreateSpiderContext($data: CreateSpiderContextInput!) {
                createSpider(data: $data) {
                    spiderName
                    latestArticleId
                    extraInfo
                    updatedAt
                }
            }
        """
        requests.post(
            self.graphql_endpoint,
            json={
                "query": create_spider_context_mutation,
                "variables": {
                    "data": data
                }
            }
        )

    def update_spider_context(self, spider_name, data):
        update_spider_context_mutation = """
            mutation UpdateSpiderContext($spiderName: String!, $data: UpdateSpiderContextInput!) {
                updateSpider(
                    where: { spiderName: $spiderName }
                    data: $data
                ) {
                    spiderName
                    latestArticleId
                    extraInfo
                    updatedAt
                }
            }
        """
        requests.post(
            self.graphql_endpoint,
            json={
                "query": update_spider_context_mutation,
                "variables": {
                    "spiderName": spider_name,
                    "data": data
                }
            }
        )


if __name__ == '__main__':
    cms_client = CMSClient(
        graphql_endpoint="https://cms.gen3.network/api/graphql",
        identity=os.getenv("CMS_IDENTITY"),
        secret=os.getenv("CMS_PASSWORD")
    )
    if cms_client.login():
        crawler_data = cms_client.get_spider_context_or_none("solana_news")
        print(crawler_data)
