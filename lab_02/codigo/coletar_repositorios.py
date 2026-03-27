import requests
import pandas as pd
import time
import os

TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {TOKEN}"
}

OUTPUT_PATH = "../dados/repos_java_top1000.csv"

repos = []
page = 1

# Se já existir arquivo, continua de onde parou
if os.path.exists(OUTPUT_PATH):
    df_existente = pd.read_csv(OUTPUT_PATH)
    repos = df_existente.to_dict("records")
    page = len(repos) // 100 + 1
    print(f"Retomando da página {page}, já temos {len(repos)} repos.")

os.makedirs("../dados", exist_ok=True)

while len(repos) < 1000:
    url = (
        "https://api.github.com/search/repositories"
        f"?q=language:java&sort=stars&order=desc&page={page}&per_page=100"
    )

    print(f"\nBuscando página {page}...")

    response = requests.get(url, headers=HEADERS)

    # 🔥 TRATAMENTO DE RATE LIMIT
    if response.status_code == 403:
        print("⚠️ Rate limit atingido. Aguardando 60 segundos...")
        time.sleep(60)
        continue

    if response.status_code != 200:
        print("Erro:", response.status_code)
        print(response.text)
        break

    data = response.json()
    items = data.get("items", [])

    if not items:
        print("Sem mais resultados.")
        break

    for item in items:
        repos.append({
            "full_name": item["full_name"],
            "clone_url": item["clone_url"],
            "stars": item["stargazers_count"],
            "html_url": item["html_url"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        })

        if len(repos) >= 1000:
            break

    print(f"Total coletado: {len(repos)}")

    # salva parcial sempre (muito importante)
    pd.DataFrame(repos).to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    page += 1
    time.sleep(2)  # pequena pausa para evitar bloqueio

print("\n✅ Coleta finalizada!")