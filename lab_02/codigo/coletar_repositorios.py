import requests
import csv
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com/search/repositories"


def calculate_time_diff(from_date):
    if not from_date:
        return "N/A"
    
    created_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)

    diff = now - created_date    
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30
    
    if years > 0:
        return f"{years} anos, {months} meses"
    elif months > 0:
        return f"{months} meses, {days} dias"
    else:
        return f"{days} dias"


def format_disk_size(kb_size):
    if not kb_size:
        return "N/A"
    
    if kb_size >= 1024 * 1024:
        return f"{kb_size / (1024 * 1024):.1f} GB"
    elif kb_size >= 1024:
        return f"{kb_size / 1024:.1f} MB"
    else:
        return f"{kb_size} KB"


def fetch_github_repos():
    all_repos = []
    page = 1
    per_page = 100  # máximo permitido
    
    while len(all_repos) < 1000:
        params = {
            "q": "language:Java maven in:description,readme",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                items = data.get("items", [])
                if not items:
                    break

                for repo in items:
                    all_repos.append({
                        "name_with_owner": repo["full_name"],
                        "url": repo["html_url"],
                        "stargazer_count": repo["stargazers_count"],
                        "primary_language": repo["language"],
                        "created_at": repo["created_at"],
                        "age": calculate_time_diff(repo["created_at"]),
                        "last_push": repo["pushed_at"],
                        "time_since_last_push": calculate_time_diff(repo["pushed_at"]),
                        "disk_usage_kb": repo["size"],
                        "size_formatted": format_disk_size(repo["size"]),
                        "name": repo["name"],
                        "releases_count": "N/A"  # REST não traz direto
                    })

                print(f"Página {page}: {len(all_repos)} repositórios coletados")

                page += 1
                time.sleep(2)

            elif response.status_code == 403:
                print("Rate limit atingido. Aguardando...")
                time.sleep(60)

            else:
                print(f"Erro: {response.status_code}")
                print(response.text)
                break

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            time.sleep(5)

    return all_repos[:1000]


def save_to_csv(repos):
    if not repos:
        print("Nenhum repositório para salvar.")
        return
    
    script_dir = Path(__file__).parent
    csv_dir = script_dir / 'dados'
    
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    filename = csv_dir / 'repos_java_top1000.csv'

    if filename.exists():
        os.remove(filename)
    
    fieldnames = [
        'name_with_owner', 
        'url', 
        'stargazer_count', 
        'primary_language',
        'created_at',
        'age',
        'last_push',
        'time_since_last_push',
        'disk_usage_kb',
        'size_formatted',
        'name',
        'releases_count'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for repo in repos:
            writer.writerow(repo)
    
    print(f"Arquivo salvo em: {filename}")
    print(f"Total: {len(repos)} repositórios")


def main():
    print("Buscando repositórios Java Maven (REST API)...")
    
    repos = fetch_github_repos()
    
    if repos:
        save_to_csv(repos)
        print(f"\nTotal coletado: {len(repos)}")
    else:
        print("Nenhum repositório encontrado.")


if __name__ == "__main__":
    main()