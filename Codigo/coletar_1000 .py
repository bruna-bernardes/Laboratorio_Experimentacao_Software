import os
import json
import time
import random
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "lab-experimentacao-software"
}

QUERY = """
query ($first: Int!, $after: String) {
  search(query: "stars:>0 sort:stars-desc", type: REPOSITORY, first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on Repository {
        id
        nameWithOwner
        url
        stargazerCount
        createdAt
        pushedAt
        primaryLanguage { name }
      }
    }
  }
}
"""

def post(query, variables):

    wait = 5

    while True:

        r = requests.post(
            URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=60
        )

        if r.status_code == 502:
            print(f"502 Bad Gateway — esperando {wait}s...")
            time.sleep(wait + random.uniform(0,2))
            wait = min(wait*2,60)
            continue

        if r.status_code != 200:
            print(r.status_code, r.text)
            raise RuntimeError("Erro na API")

        data = r.json()

        if "errors" in data:
            print(data["errors"])
            raise RuntimeError("Erro GraphQL")

        return data["data"]


repos = []
after = None

while len(repos) < 1000:

    data = post(QUERY, {"first":100,"after":after})

    search = data["search"]

    repos.extend(search["nodes"])

    after = search["pageInfo"]["endCursor"]

    print("Repos coletados:", len(repos))

    if not search["pageInfo"]["hasNextPage"]:
        break


repos = repos[:1000]

os.makedirs("lab_01/Relatorios/Dados",exist_ok=True)

with open("lab_01/Relatorios/Dados/repos_1000.json","w",encoding="utf-8") as f:
    json.dump(repos,f,indent=2,ensure_ascii=False)

print("JSON 1000 criado")


df = pd.DataFrame(repos)

df.to_csv(
    "lab_01/Relatorios/Dados/repos_1000.csv",
    index=False,
    encoding="utf-8"
)

print("CSV criado com sucesso")