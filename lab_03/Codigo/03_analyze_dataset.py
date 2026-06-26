import os
import pandas as pd
from scipy.stats import spearmanr

DATA_DIR = "data"
OUTPUT_DIR = "output"
RAW_FILE = os.path.join(DATA_DIR, "pulls_raw.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "summary.csv")
RQ_FILE = os.path.join(DATA_DIR, "rq_results.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def spearman_safe(x, y):
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(df) < 3:
        return None, None
    coef, p = spearmanr(df["x"], df["y"])
    return coef, p

def main():
    df = pd.read_csv(RAW_FILE)

    metrics = [
        "changed_files",
        "additions",
        "deletions",
        "review_time_hours",
        "description_length",
        "participants_count",
        "comments_count",
        "review_count"
    ]

    summary_rows = []
    for col in metrics:
        summary_rows.append({
            "metric": col,
            "median_all": df[col].median(),
            "median_merged": df[df["final_status"] == "MERGED"][col].median(),
            "median_closed": df[df["final_status"] == "CLOSED"][col].median()
        })

    pd.DataFrame(summary_rows).to_csv(SUMMARY_FILE, index=False)

    rq_rows = []
    for col in [
        "changed_files", "additions", "deletions",
        "review_time_hours", "description_length",
        "participants_count", "comments_count"
    ]:
        coef_status, p_status = spearman_safe(df[col], df["merged_binary"])
        rq_rows.append({
            "rq_group": "Status do PR",
            "metric": col,
            "spearman": coef_status,
            "p_value": p_status
        })

    for col in [
        "changed_files", "additions", "deletions",
        "review_time_hours", "description_length",
        "participants_count", "comments_count"
    ]:
        coef_reviews, p_reviews = spearman_safe(df[col], df["review_count"])
        rq_rows.append({
            "rq_group": "Número de revisões",
            "metric": col,
            "spearman": coef_reviews,
            "p_value": p_reviews
        })

    pd.DataFrame(rq_rows).to_csv(RQ_FILE, index=False)

    print(f"Resumo salvo em: {SUMMARY_FILE}")
    print(f"Resultados das RQs salvos em: {RQ_FILE}")

if __name__ == "__main__":
    main()