import os
import csv
import json
import time
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKENS = [
    t for t in [
        os.environ.get("GITHUB_TOKEN_1", ""),
        os.environ.get("GITHUB_TOKEN_2", ""),
        os.environ.get("GITHUB_TOKEN_3", ""),
        os.environ.get("GITHUB_TOKEN_4", ""),
    ] if t
]
if not TOKENS:
    raise SystemExit("Set GITHUB_TOKEN_1-4 env vars")

GQL_URL = "https://api.github.com/graphql"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
ERRORS_FILE = os.path.join(DATA_DIR, "errors_new.csv")
REPOS_FILE = os.path.join(DATA_DIR, "repos.csv")
PULLS_FILE = os.path.join(DATA_DIR, "pulls_raw.csv")

MAX_RETRIES = 8
RETRY_DELAY = 10
MAX_PRS_PER_REPO = 1000

write_lock = threading.Lock()
print_lock = threading.Lock()

token_index = 0
token_lock = threading.Lock()


def get_next_token():
    global token_index
    with token_lock:
        idx = token_index % len(TOKENS)
        token_index += 1
    return TOKENS[idx]


def tprint(msg):
    with print_lock:
        print(msg, flush=True)


def graphql_query(query):
    for attempt in range(1, MAX_RETRIES + 1):
        token = get_next_token()
        headers = {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(GQL_URL, headers=headers, json={"query": query}, timeout=90)
        except requests.exceptions.RequestException as e:
            tprint(f"  Network error attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            continue

        if resp.status_code == 200:
            data = resp.json()
            if "errors" in data:
                msgs = "; ".join(e.get("message", "")[:60] for e in data["errors"][:3])
                if "rate limit" in msgs.lower() or "abuse" in msgs.lower():
                    tprint(f"  Rate limited, sleeping 30s...")
                    time.sleep(30)
                    continue
                tprint(f"  GQL errors: {msgs}")
            return data

        if resp.status_code == 403:
            reset = int(resp.headers.get("X-RateLimit-Reset", 0))
            if reset:
                sleep_time = max(reset - int(time.time()), 0) + 5
                tprint(f"  403 rate limited, sleeping {sleep_time}s")
                time.sleep(sleep_time)
            else:
                time.sleep(60)
            continue

        if resp.status_code >= 500:
            time.sleep(RETRY_DELAY * attempt)
            continue

        tprint(f"  HTTP {resp.status_code}")
        return None

    return None


def fetch_prs_page(owner, repo, after_cursor=None, page_size=25):
    after_clause = f', after: "{after_cursor}"' if after_cursor else ""
    query = f"""{{
  repository(owner: "{owner}", name: "{repo}") {{
    pullRequests(states: [MERGED, CLOSED], first: {page_size}, orderBy: {{field: CREATED_AT, direction: DESC}}{after_clause}) {{
      pageInfo {{ hasNextPage endCursor }}
      nodes {{
        number, title, state, mergedAt, closedAt, createdAt,
        changedFiles, additions, deletions, bodyText,
        comments {{ totalCount }},
        participants {{ totalCount }},
        reviews {{ totalCount }}
      }}
    }}
  }}
}}"""
    result = graphql_query(query)
    if not result or "data" not in result or not result["data"].get("repository"):
        return None, None, False
    pr_data = result["data"]["repository"]["pullRequests"]
    return pr_data["nodes"], pr_data["pageInfo"]["endCursor"], pr_data["pageInfo"]["hasNextPage"]


def process_pr_node(node, repo_full_name):
    if not node:
        return None
    state = node.get("state", "")
    if state == "MERGED":
        final_status = "MERGED"
        merged_binary = 1
        final_at = node.get("mergedAt") or node.get("closedAt") or ""
    else:
        final_status = "CLOSED"
        merged_binary = 0
        final_at = node.get("closedAt") or ""

    created_at = node.get("createdAt", "")
    if not created_at or not final_at:
        return None

    try:
        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        final_dt = datetime.fromisoformat(final_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

    review_time_hours = (final_dt - created_dt).total_seconds() / 3600.0
    if review_time_hours <= 1.0:
        return None

    review_count = node.get("reviews", {}).get("totalCount", 0)
    if review_count < 1:
        return None

    body = node.get("bodyText") or ""
    return {
        "repo": repo_full_name,
        "pr_number": node.get("number"),
        "title": node.get("title", ""),
        "author": "",
        "final_status": final_status,
        "merged_binary": merged_binary,
        "created_at": created_at,
        "final_at": final_at,
        "review_time_hours": round(review_time_hours, 4),
        "changed_files": node.get("changedFiles", 0),
        "additions": node.get("additions", 0),
        "deletions": node.get("deletions", 0),
        "description_length": len(body),
        "participants_count": node.get("participants", {}).get("totalCount", 0),
        "comments_count": node.get("comments", {}).get("totalCount", 0),
        "review_count": review_count,
    }


def collect_prs_for_repo(repo_full_name):
    owner, repo = repo_full_name.split("/")
    all_rows = []
    after_cursor = None
    total_collected = 0

    for _ in range(50):
        nodes, end_cursor, has_next = fetch_prs_page(owner, repo, after_cursor=after_cursor)
        if nodes is None:
            break
        if not nodes:
            break

        for node in nodes:
            row = process_pr_node(node, repo_full_name)
            if row:
                all_rows.append(row)
                total_collected += 1

        if not has_next:
            break
        after_cursor = end_cursor
        if total_collected >= MAX_PRS_PER_REPO:
            break

    return all_rows


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("processed_repos", []))
    return set()


def save_progress(processed):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"processed_repos": sorted(processed)}, f, indent=2)


def log_error(repo, stage, error):
    with write_lock:
        file_exists = os.path.exists(ERRORS_FILE)
        with open(ERRORS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["repo", "stage", "error"])
            writer.writerow([repo, stage, str(error)[:500]])


def main():
    processed = load_progress()
    existing_pr_repos = set()
    if os.path.exists(PULLS_FILE):
        with open(PULLS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_pr_repos.add(row["repo"])

    repos = []
    with open(REPOS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            repo = row["repo"]
            total_prs = int(row.get("total_prs_merged_closed", 0))
            if total_prs < 100:
                continue
            if repo in processed:
                continue
            if repo in existing_pr_repos:
                continue
            repos.append((repo, total_prs))

    repos.sort(key=lambda x: -x[1])
    tprint(f"Tokens: {len(TOKENS)} | Repos to process: {len(repos)}")

    fieldnames = [
        "repo", "pr_number", "title", "author", "final_status", "merged_binary",
        "created_at", "final_at", "review_time_hours", "changed_files",
        "additions", "deletions", "description_length", "participants_count",
        "comments_count", "review_count",
    ]

    MAX_WORKERS = 8
    completed = 0
    total = len(repos)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_repo = {
            executor.submit(collect_prs_for_repo, repo): (repo, total_prs)
            for repo, total_prs in repos
        }
        for future in as_completed(future_to_repo):
            repo, total_prs = future_to_repo[future]
            completed += 1
            try:
                rows = future.result()
                if rows:
                    with write_lock:
                        file_exists = os.path.exists(PULLS_FILE)
                        with open(PULLS_FILE, "a", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            if not file_exists:
                                writer.writeheader()
                            writer.writerows(rows)
                    tprint(f"[{completed}/{total}] {repo}: {len(rows)} PRs")
                else:
                    tprint(f"[{completed}/{total}] {repo}: 0 PRs (filtered)")
                processed.add(repo)
                with write_lock:
                    save_progress(processed)
            except Exception as e:
                tprint(f"[{completed}/{total}] {repo}: Error - {e}")
                log_error(repo, "collect_prs_graphql", str(e))

    tprint(f"\nDone! {len(processed)} repos processed.")
    with open(PULLS_FILE, "r", encoding="utf-8") as f:
        total_rows = sum(1 for _ in csv.DictReader(f))
    tprint(f"Total rows in CSV: {total_rows}")


if __name__ == "__main__":
    main()