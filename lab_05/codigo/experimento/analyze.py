import pandas as pd
import numpy as np
from scipy import stats
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_CSV = os.path.join(PROJECT_ROOT, "dados", "raw", "resultados.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dados", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALPHA = 0.05

df = pd.read_csv(RESULTS_CSV)
df = df[df["response_time_ms"] > 0].copy()

print("=" * 70)
print("ANALISE ESTATISTICA - GraphQL vs REST")
print("=" * 70)

summary_rows = []

for complexity in ["simples", "media", "complexa"]:
    for metric, col in [("tempo", "response_time_ms"), ("tamanho", "response_size_bytes")]:
        for api in ["REST", "GraphQL"]:
            subset = df[(df["complexity"] == complexity) & (df["api"] == api)]
            values = subset[col].values
            summary_rows.append({
                "complexidade": complexity,
                "metrica": metric,
                "api": api,
                "n": len(values),
                "media": round(np.mean(values), 3),
                "mediana": round(np.median(values), 3),
                "desvio_padrao": round(np.std(values, ddof=1), 3),
                "minimo": round(np.min(values), 3),
                "maximo": round(np.max(values), 3),
                "q1": round(np.percentile(values, 25), 3),
                "q3": round(np.percentile(values, 75), 3),
            })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(OUTPUT_DIR, "estatisticas_descritivas.csv"), index=False)
summary_df.to_markdown(os.path.join(OUTPUT_DIR, "estatisticas_descritivas.md"), index=False)
print("\nEstatisticas descritivas salvas.")
print(summary_df.to_string(index=False))

print("\n" + "=" * 70)
print("TESTE DE NORMALIDADE (Shapiro-Wilk)")
print("=" * 70)

normality_results = []

for complexity in ["simples", "media", "complexa"]:
    for metric, col in [("tempo", "response_time_ms"), ("tamanho", "response_size_bytes")]:
        for api in ["REST", "GraphQL"]:
            subset = df[(df["complexity"] == complexity) & (df["api"] == api)]
            values = subset[col].values
            if len(values) >= 3:
                stat, p = stats.shapiro(values)
                normal = p > ALPHA
                normality_results.append({
                    "complexidade": complexity,
                    "metrica": metric,
                    "api": api,
                    "shapiro_stat": round(stat, 4),
                    "p_valor": f"{p:.6f}",
                    "normal": "Sim" if normal else "Nao",
                })
                print(f"  {complexity}/{metric}/{api}: W={stat:.4f}, p={p:.6f} -> {'Normal' if normal else 'Nao normal'}")

normality_df = pd.DataFrame(normality_results)
normality_df.to_csv(os.path.join(OUTPUT_DIR, "teste_normalidade.csv"), index=False)

print("\n" + "=" * 70)
print("TESTES DE HIPOTESE - RQ1 (Tempo de Resposta) e RQ2 (Tamanho da Resposta)")
print("=" * 70)

hypothesis_results = []

for complexity in ["simples", "media", "complexa"]:
    for metric, col, rq in [("tempo", "response_time_ms", "RQ1"), ("tamanho", "response_size_bytes", "RQ2")]:
        rest_vals = df[(df["complexity"] == complexity) & (df["api"] == "REST")][col].values
        gql_vals = df[(df["complexity"] == complexity) & (df["api"] == "GraphQL")][col].values

        u_stat, u_p = stats.mannwhitneyu(rest_vals, gql_vals, alternative="two-sided")

        rest_median = np.median(rest_vals)
        gql_median = np.median(gql_vals)
        rest_mean = np.mean(rest_vals)
        gql_mean = np.mean(gql_vals)

        effect_size_r = abs(u_stat) / np.sqrt(len(rest_vals) * len(gql_vals))

        if gql_median < rest_median:
            direction = "GraphQL < REST"
        elif gql_median > rest_median:
            direction = "GraphQL > REST"
        else:
            direction = "GraphQL = REST"

        significant = "Sim" if u_p < ALPHA else "Nao"

        p_display = "< 0.001" if u_p < 0.001 else f"{u_p:.4f}"

        hypothesis_results.append({
            "RQ": rq,
            "complexidade": complexity,
            "metrica": metric,
            "rest_mediana": round(rest_median, 3),
            "graphql_mediana": round(gql_median, 3),
            "rest_media": round(rest_mean, 3),
            "graphql_media": round(gql_mean, 3),
            "diferenca_mediana_pct": round(((gql_median - rest_median) / rest_median) * 100, 2),
            "mann_whitney_U": round(u_stat, 2),
            "p_valor": p_display,
            "p_valor_num": float(u_p),
            "significativo": significant,
            "direcao": direction,
            "tamanho_efeito_r": round(effect_size_r, 4),
        })

        print(f"\n{rq} - {metric} - Complexidade: {complexity}")
        print(f"  REST mediana: {rest_median:.3f}, GraphQL mediana: {gql_median:.3f}")
        print(f"  REST media: {rest_mean:.3f}, GraphQL media: {gql_mean:.3f}")
        print(f"  Diferenca: {((gql_median - rest_median) / rest_median) * 100:.2f}%")
        print(f"  Mann-Whitney U={u_stat:.2f}, p={p_display} -> {significant}")
        print(f"  Direcao: {direction}")
        print(f"  Tamanho de efeito r: {effect_size_r:.4f}")

hypothesis_df = pd.DataFrame(hypothesis_results)
hypothesis_df.to_csv(os.path.join(OUTPUT_DIR, "testes_hipotese.csv"), index=False)
hypothesis_df.to_markdown(os.path.join(OUTPUT_DIR, "testes_hipotese.md"), index=False)

print("\n" + "=" * 70)
print("RESPOSTAS AS PERGUNTAS DE PESQUISA")
print("=" * 70)

rq1_rows = hypothesis_df[hypothesis_df["RQ"] == "RQ1"]
print("\nRQ1: Respostas as consultas GraphQL sao mais rapidas que respostas as consultas REST?")
for _, row in rq1_rows.iterrows():
    print(f"  Complexidade {row['complexidade']}: {row['direcao']} (p={row['p_valor']}, significativo={row['significativo']})")
    if row['significativo'] == "Sim":
        if "GraphQL < REST" in row["direcao"]:
            print(f"    -> GraphQL e MAIS RAPIDO em {row['complexidade']}")
        else:
            print(f"    -> REST e MAIS RAPIDO em {row['complexidade']}")
    else:
        print(f"    -> Nao ha diferenca significativa em {row['complexidade']}")

rq2_rows = hypothesis_df[hypothesis_df["RQ"] == "RQ2"]
print("\nRQ2: Respostas as consultas GraphQL tem tamanho menor que respostas as consultas REST?")
for _, row in rq2_rows.iterrows():
    print(f"  Complexidade {row['complexidade']}: {row['direcao']} (p={row['p_valor']}, significativo={row['significativo']})")
    if row['significativo'] == "Sim":
        if "GraphQL < REST" in row["direcao"]:
            print(f"    -> GraphQL tem resposta MENOR em {row['complexidade']}")
        else:
            print(f"    -> REST tem resposta MENOR em {row['complexidade']}")
    else:
        print(f"    -> Nao ha diferenca significativa em {row['complexidade']}")

results_json = {
    "estatisticas_descritivas": summary_df.to_dict(orient="records"),
    "teste_normalidade": normality_df.to_dict(orient="records"),
    "testes_hipotese": hypothesis_df.to_dict(orient="records"),
    "alpha": ALPHA,
}

with open(os.path.join(OUTPUT_DIR, "analysis_results.json"), "w") as f:
    json.dump(results_json, f, indent=2, ensure_ascii=False)

print(f"\nResultados salvos em: {OUTPUT_DIR}")
print("  - estatisticas_descritivas.csv/.md")
print("  - teste_normalidade.csv")
print("  - testes_hipotese.csv/.md")
print("  - analysis_results.json")