import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

QUERY = """
query($cursor: String) {
  search(
    query: "stars:>1000 sort:stars-desc archived:false is:public",
    type: REPOSITORY,
    first: 100,
    after: $cursor
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        pullRequests(states: [MERGED, CLOSED]) {
          totalCount
        }
      }
    }
  }
}
"""

def run_query(query, variables=None):
    r = requests.post(URL, json={"query": query, "variables": variables or {}}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise Exception(data["errors"])
    return data["data"]

def main():
    os.makedirs("data", exist_ok=True)

    repos = []
    cursor = None

    while len(repos) < 250:
        data = run_query(QUERY, {"cursor": cursor})
        result = data["search"]

        for node in result["nodes"]:
            repos.append({
                "repo": node["nameWithOwner"],
                "stars": node["stargazerCount"],
                "total_prs_merged_closed": node["pullRequests"]["totalCount"]
            })

        if not result["pageInfo"]["hasNextPage"]:
            break

        cursor = result["pageInfo"]["endCursor"]
        time.sleep(1)

    df = pd.DataFrame(repos)
    df = df[df["total_prs_merged_closed"] >= 100].drop_duplicates(subset=["repo"])
    df = df.sort_values(["stars", "total_prs_merged_closed"], ascending=[False, False]).head(200)
    df.to_csv("data/repos.csv", index=False)

    print(f"{len(df)} repositórios salvos em data/repos.csv")

if __name__ == "__main__":
    main()