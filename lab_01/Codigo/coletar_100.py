import os, json, time, random
import requests
from dotenv import load_dotenv

URL = "https://api.github.com/graphql"

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

def post(headers, variables):
    wait = 5
    while True:
        r = requests.post(URL, json={"query": QUERY, "variables": variables}, headers=headers, timeout=60)
        if r.status_code == 502:
            print(f"502 — esperando {wait}s...")
            time.sleep(wait + random.uniform(0, 2))
            wait = min(wait * 2, 60)
            continue
        if r.status_code != 200:
            print(r.status_code, r.text[:1200])
            raise RuntimeError("Erro na API")
        data = r.json()
        if "errors" in data:
            print(data["errors"])
            raise RuntimeError("Erro GraphQL")
        return data["data"]

def main():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "lab-experimentacao-software"
    }

    data = post(headers, {"first": 100, "after": None})
    repos = data["search"]["nodes"]

    os.makedirs("lab_01/Relatorios/Dados", exist_ok=True)
    with open("lab_01/Relatorios/Dados/repos_100_leve.json", "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)

    print(f"✅ Sprint 1 OK: {len(repos)} repos salvos.")

if __name__ == "__main__":
    main()
