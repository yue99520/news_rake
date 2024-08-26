import os
import requests
from datetime import datetime

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

    def prepare_crawler_data(self):
        return {
            "newsTopicCN": "1",
            "newsTopicEN": "1",
            "platformName": "1",
            "URL": "1",
            "contentCN": "1",
            "contentEN": "1",
            "date": datetime.now().isoformat() + "Z",  # Current date-time in UTC
            "language": "zh"
        }

    def create_crawler(self, data):
        create_crawler_mutation = """
        mutation ($data: CrawlerCreateInput!) {
          item: createCrawler(data: $data) {
            id
            label: id
            __typename
          }
        }
        """
        response = self.session.post(
            self.graphql_endpoint,
            json={"query": create_crawler_mutation, "variables": {"data": data}}
        )

        if response.status_code == 200:
            print("Mutation successful!")
            print(response.json())
        else:
            print("Mutation failed!")
            print(response.text)

# Example usage
if __name__ == "__main__":
    cms_client = CMSClient(
        graphql_endpoint="https://cms.gen3.network/api/graphql",
        identity=os.getenv("CMS_IDENTITY"),
        secret=os.getenv("CMS_PASSWORD")
    )

    if cms_client.login():
        crawler_data = cms_client.prepare_crawler_data()
        cms_client.create_crawler(crawler_data)
