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

QUERY_LEVE = """
query ($first: Int!, $after: String) {
  search(
    query: "stars:>0 sort:stars-desc",
    type: REPOSITORY,
    first: $first,
    after: $after
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        id
        nameWithOwner
        url
        stargazerCount
        createdAt
        pushedAt
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""

QUERY_METRICAS = """
query ($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Repository {
      id
      pullRequests(states: MERGED) {
        totalCount
      }
      releases {
        totalCount
      }
      issues {
        totalCount
      }
      closedIssues: issues(states: CLOSED) {
        totalCount
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
            time.sleep(wait + random.uniform(0, 2))
            wait = min(wait * 2, 60)
            continue

        if r.status_code == 403 and "rate limit" in r.text.lower():
            print("Rate limit atingido. Esperando 60s...")
            time.sleep(60)
            continue

        if r.status_code != 200:
            print(r.status_code, r.text)
            raise RuntimeError("Erro na API")

        data = r.json()

        if "errors" in data:
            print(f"Aviso: {len(data['errors'])} repositórios não encontrados.")

        return data["data"]


# =========================
# ETAPA 1: buscar 1000 repositórios leves
# =========================
repos = []
after = None

while len(repos) < 1000:
    data = post(QUERY_LEVE, {"first": 100, "after": after})
    search = data["search"]

    repos.extend(search["nodes"])
    after = search["pageInfo"]["endCursor"]

    print("Repos leves coletados:", len(repos))

    if not search["pageInfo"]["hasNextPage"]:
        break

repos = repos[:1000]

# dicionário por id
repos_por_id = {repo["id"]: repo for repo in repos}

# =========================
# ETAPA 2: buscar métricas em lotes pequenos
# =========================
ids = [repo["id"] for repo in repos]
lote = 20

for i in range(0, len(ids), lote):
    ids_lote = ids[i:i + lote]
    data = post(QUERY_METRICAS, {"ids": ids_lote})

    for repo in data["nodes"]:
        if repo is None:
            continue

        repo_base = repos_por_id[repo["id"]]
        repo_base["pullRequestsAccepted"] = repo["pullRequests"]["totalCount"]
        repo_base["releasesCount"] = repo["releases"]["totalCount"]
        repo_base["issuesTotal"] = repo["issues"]["totalCount"]
        repo_base["closedIssuesCount"] = repo["closedIssues"]["totalCount"]

    print(f"Métricas coletadas: {min(i + lote, len(ids))}/{len(ids)}")

# =========================
# SALVAR JSON
# =========================
os.makedirs("lab_01/Relatorios/Dados", exist_ok=True)

with open("lab_01/Relatorios/Dados/repos_1000.json", "w", encoding="utf-8") as f:
    json.dump(repos, f, indent=2, ensure_ascii=False)

print("JSON 1000 criado")

# =========================
# MONTAR CSV LIMPO
# =========================
linhas = []

for repo in repos:
    linhas.append({
        "id": repo["id"],
        "nameWithOwner": repo["nameWithOwner"],
        "url": repo["url"],
        "stargazerCount": repo["stargazerCount"],
        "createdAt": repo["createdAt"],
        "pushedAt": repo["pushedAt"],
        "primaryLanguage": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None,
        "pullRequestsAccepted": repo.get("pullRequestsAccepted"),
        "releasesCount": repo.get("releasesCount"),
        "issuesTotal": repo.get("issuesTotal"),
        "closedIssuesCount": repo.get("closedIssuesCount")
    })

df = pd.DataFrame(linhas)

df.to_csv(
    "lab_01/Relatorios/Dados/repos_1000.csv",
    index=False,
    encoding="utf-8"
)

print("CSV criado com sucesso")