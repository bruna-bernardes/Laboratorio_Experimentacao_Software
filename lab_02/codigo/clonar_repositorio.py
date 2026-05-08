import subprocess
import time
import os
import shutil
import stat
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock

# =========================
# CONFIG GLOBAL
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_DIR = os.path.join(SCRIPT_DIR, '..', 'txtFiles')
CLONE_DIR = os.path.join(SCRIPT_DIR, 'cloned_repos')

os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(CLONE_DIR, exist_ok=True)

lock = Lock()

successful_repos = []
skipped_repos_log = []

# =========================
# HELPERS
# =========================

def sanitize_folder_name(name):
    name = name.replace('/', '-')
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def find_exact_case_match(base_dir, repo_name):
    try:
        for dirname in os.listdir(base_dir):
            if dirname == repo_name:
                fullpath = os.path.join(base_dir, dirname)
                if os.path.exists(os.path.join(fullpath, '.git')):
                    return fullpath
        return None
    except:
        return None

def find_case_insensitive_conflicts(base_dir, repo_name):
    try:
        conflicts = []
        for dirname in os.listdir(base_dir):
            if dirname.lower() == repo_name.lower() and dirname != repo_name:
                conflicts.append(dirname)
        return conflicts
    except:
        return []

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except:
        pass

def safe_rmtree(path):
    try:
        shutil.rmtree(path, onerror=remove_readonly)
        return True
    except:
        return False

# =========================
# FILE SAVE
# =========================

def save_urls_to_file(urls, filename, description):
    if not urls:
        return

    filepath = os.path.join(TXT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {description}\n")
        f.write(f"# Total: {len(urls)}\n\n")
        f.write(';'.join(urls))

    print(f"[SALVO] {filepath}")

def save_skip_log(skipped_log, filename):
    if not skipped_log:
        return

    filepath = os.path.join(TXT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        for entry in skipped_log:
            f.write(f"{entry}\n")

# =========================
# CSV
# =========================

def load_repos_from_csv(csv_file_path):
    repos = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            repos.append({
                'url': row['url'],
                'name': row['name'],
                'name_with_owner': row.get('name_with_owner', row['name'])
            })
    return repos

# =========================
# CLONE
# =========================

def git_clone(repo_info):
    repo_url = repo_info['url']
    name_with_owner = repo_info['name_with_owner']

    folder_name = sanitize_folder_name(name_with_owner)
    target_path = os.path.join(CLONE_DIR, folder_name)

    # EXISTE
    if find_exact_case_match(CLONE_DIR, folder_name):
        with lock:
            skipped_repos_log.append(repo_url)
            successful_repos.append(repo_url)
        return None

    # CONFLITO
    conflicts = find_case_insensitive_conflicts(CLONE_DIR, folder_name)
    if conflicts:
        with lock:
            skipped_repos_log.append(repo_url)
        return repo_url

    # CLONE
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, target_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )

        with lock:
            successful_repos.append(repo_url)

        print(f"[OK] {folder_name}")
        return None

    except Exception:
        return repo_url

# =========================
# PARALELO
# =========================

def clone_parallel(repos, workers=4):
    total = len(repos)
    chunk_size = max(1, total // workers)

    chunks = [
        repos[i:i + chunk_size]
        for i in range(0, total, chunk_size)
    ]

    failures = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

        for f in as_completed(futures):
            failures.extend(f.result())

    return failures

def process_chunk(chunk):
    failures = []
    for repo in chunk:
        result = git_clone(repo)
        if result:
            failures.append(result)
    return failures

# =========================
# MAIN
# =========================

def main():
    csv_path = os.path.join(SCRIPT_DIR, '..', 'dados', 'repos_java_top1000.csv')

    repos = load_repos_from_csv(csv_path)

    print(f"[INFO] Clonando {len(repos)} repositórios...")

    failures = clone_parallel(repos, workers=4)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    save_urls_to_file(successful_repos, f"success_{timestamp}.txt", "Sucesso")
    save_urls_to_file(failures, f"fail_{timestamp}.txt", "Falhas")
    save_skip_log(skipped_repos_log, f"skip_{timestamp}.txt")

    print("\n===== FINAL =====")
    print(f"Sucesso: {len(successful_repos)}")
    print(f"Falhas: {len(failures)}")
    print(f"Skip: {len(skipped_repos_log)}")

if __name__ == "__main__":
    main()