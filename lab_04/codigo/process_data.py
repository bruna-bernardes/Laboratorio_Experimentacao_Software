import pickle
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import json

CHECKPOINTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "checkpoints"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dados", "processed"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

BOT_PATTERNS = [
    "dependabot", "renovate", "github-actions", "codecov", "snyk",
    "greenkeeper", "pyup-bot", "bitrise-io", "circleci", "travis-ci",
    "appveyor", "coveralls", "semantic-release", "netlify", "vercel",
    "stale", "lock", "mergify", "pre-commit-ci", "changeset-bot",
    "graphql-inspector", "oss-review-kit", "cla-assistant", "imgbot",
    "allcontributors", "sentry-io", "codacy-production", "meilisearch",
    "typescript-bot", "eslint-bot", "tslint-bot", "angular-cli-bot",
    "msftbot", "github-advanced-security", "mention-bot", "ms-resource-bot",
]

MAIN_BRANCHES = {"main", "master"}


def is_bot_fast(author, author_type):
    if author_type == "Bot":
        return True
    if author is None:
        return True
    a = str(author).lower()
    for p in BOT_PATTERNS:
        if p in a:
            return True
    return False


def parse_ts(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return pd.NaT
    try:
        return pd.Timestamp(val)
    except Exception:
        return pd.NaT


print("Carregando dados dos checkpoints...")
all_rows = []
files = sorted(f for f in os.listdir(CHECKPOINTS_DIR) if f.endswith(".pkl"))
total_files = len(files)

for i, fname in enumerate(files):
    fpath = os.path.join(CHECKPOINTS_DIR, fname)
    with open(fpath, "rb") as fh:
        data = pickle.load(fh)
    all_rows.extend(data.get("rows", []))
    if (i + 1) % 50 == 0 or (i + 1) == total_files:
        print(f"  {i+1}/{total_files} arquivos, {len(all_rows):,} PRs")

print(f"Total de PRs brutas: {len(all_rows):,}")
df = pd.DataFrame(all_rows)
del all_rows
initial_count = len(df)

print("Filtrando bots...")
df["is_bot"] = df.apply(lambda r: is_bot_fast(r.get("author"), r.get("author_type")), axis=1)
bots_removed = int(df["is_bot"].sum())
df = df[~df["is_bot"]].copy()

print("Filtrando author nulo...")
df = df[df["author"].notna()].copy()

print("Filtrando datas validas...")
df["created_at_ts"] = df["created_at"].apply(parse_ts)
df = df[df["created_at_ts"].notna()].copy()

print("Filtrando branches principais...")
df["base_branch_lower"] = df["base_branch"].astype(str).str.lower().str.strip()
df = df[df["base_branch_lower"].isin(MAIN_BRANCHES)].copy()

removed = initial_count - len(df)
print(f"Limpeza: removidas {removed:,} PRs ({removed/initial_count*100:.1f}%)")
print(f"Dataset apos limpeza: {len(df):,} PRs em {df['repo'].nunique()} repos")

print("Calculando metricas derivadas...")
df["first_response_at_ts"] = df["first_response_at"].apply(parse_ts)
df["closed_at_ts"] = df["closed_at"].apply(parse_ts)
df["merged_at_ts"] = df["merged_at"].apply(parse_ts)
df["updated_at_ts"] = df["updated_at"].apply(parse_ts)
df["last_activity_at_ts"] = df["last_activity_at"].apply(parse_ts)

now = pd.Timestamp.now(tz=timezone.utc)

print("Classificando abandono...")
df["abandoned"] = 0
open_mask = df["state"] == "open"
if open_mask.sum() > 0:
    ref_dates = df.loc[open_mask, "last_activity_at_ts"].fillna(
        df.loc[open_mask, "updated_at_ts"]
    )
    days_inactive = (now - ref_dates).dt.days
    df.loc[open_mask, "abandoned"] = (days_inactive > 30).astype(int)

print("Calculando tempo ate primeira resposta...")
df["time_to_first_response_h"] = np.nan
has_resp = df["first_response_at_ts"].notna() & df["created_at_ts"].notna()
if has_resp.sum() > 0:
    diff_h = (df.loc[has_resp, "first_response_at_ts"] - df.loc[has_resp, "created_at_ts"]).dt.total_seconds() / 3600.0
    df.loc[has_resp, "time_to_first_response_h"] = diff_h.where(diff_h >= 0, np.nan)

df["total_lines"] = df["additions"] + df["deletions"]
df["state_label"] = df["state"].map({"merged": "Merged", "closed": "Closed", "open": "Open"})

df["participants_bucket"] = pd.cut(
    df["participants_count"],
    bins=[-1, 0, 2, 5, float("inf")],
    labels=["0", "1-2", "3-5", ">5"]
)

df["response_time_bucket"] = "Sem resposta"
has_time = df["time_to_first_response_h"].notna()
df.loc[has_time & (df["time_to_first_response_h"] <= 72), "response_time_bucket"] = "<=72h"
df.loc[has_time & (df["time_to_first_response_h"] > 72), "response_time_bucket"] = ">72h"

output_cols = [
    "repo", "language", "pr_id", "pr_number", "author", "author_type",
    "state", "state_label", "abandoned",
    "created_at_ts", "closed_at_ts", "merged_at_ts", "updated_at_ts",
    "first_response_at_ts", "last_activity_at_ts",
    "time_to_first_response_h", "response_time_bucket",
    "comments_count", "review_comments_count", "reviews_count",
    "participants_count", "participants_bucket",
    "additions", "deletions", "total_lines", "changed_files", "commits",
    "base_branch"
]
col_names = [
    "repo", "language", "pr_id", "pr_number", "author", "author_type",
    "state", "state_label", "abandoned",
    "created_at", "closed_at", "merged_at", "updated_at",
    "first_response_at", "last_activity_at",
    "time_to_first_response_h", "response_time_bucket",
    "comments_count", "review_comments_count", "reviews_count",
    "participants_count", "participants_bucket",
    "additions", "deletions", "total_lines", "changed_files", "commits",
    "base_branch"
]

df_export = df[output_cols].copy()
df_export.columns = col_names

output_csv = os.path.join(OUTPUT_DIR, "prs_processed.csv")
print(f"Salvando CSV...")
df_export.to_csv(output_csv, index=False)
print(f"CSV salvo em: {output_csv}")

abandoned_count = int(df_export["abandoned"].sum())
total = len(df_export)
state_counts = df_export["state_label"].value_counts().to_dict()

stats = {
    "total_prs": total,
    "abandoned": abandoned_count,
    "not_abandoned": total - abandoned_count,
    "abandonment_rate": round(abandoned_count / total * 100, 1),
    "repos": int(df_export["repo"].nunique()),
    "bots_removed": bots_removed,
    "total_removed": removed,
    "removed_pct": round(removed / initial_count * 100, 1),
    "states": state_counts,
}
with open(os.path.join(OUTPUT_DIR, "dataset_stats.json"), "w") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

repo_stats = df_export.groupby("repo").agg(
    total=("pr_id", "count"),
    abandoned=("abandoned", "sum"),
).reset_index()
repo_stats["abandonment_rate"] = (repo_stats["abandoned"] / repo_stats["total"] * 100).round(2)
repo_stats = repo_stats.sort_values("total", ascending=False)
repo_stats.to_csv(os.path.join(OUTPUT_DIR, "repo_stats.csv"), index=False)

print(f"\n=== RESUMO ===")
print(f"PRs totais: {total:,}")
print(f"PRs abandonadas: {abandoned_count:,} ({abandoned_count/total*100:.1f}%)")
print(f"PRs nao abandonadas: {total-abandoned_count:,} ({(total-abandoned_count)/total*100:.1f}%)")
print(f"Repositorios: {df_export['repo'].nunique()}")
for state, count in state_counts.items():
    print(f"  {state}: {count:,} ({count/total*100:.1f}%)")
print(f"\nTop 5 maior taxa abandono:")
for _, r in repo_stats.nlargest(5, "abandonment_rate").iterrows():
    print(f"  {r['repo']}: {r['abandonment_rate']:.1f}%")
print(f"Top 5 menor taxa abandono:")
for _, r in repo_stats.nsmallest(5, "abandonment_rate").iterrows():
    print(f"  {r['repo']}: {r['abandonment_rate']:.1f}%")