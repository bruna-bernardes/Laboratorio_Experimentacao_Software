import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "dados")
RESULTS_CSV = os.path.join(DATA_DIR, "raw", "resultados.csv")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = PROCESSED_DIR

COMPLEXITY_ORDER = ["simples", "media", "complexa"]
COMPLEXITY_LABELS = {"simples": "Simples", "media": "Media", "complexa": "Complexa"}
API_COLORS = {"REST": "#E74C3C", "GraphQL": "#3498DB"}

df = pd.read_csv(RESULTS_CSV)
df = df[df["response_time_ms"] > 0].copy()

with open(os.path.join(PROCESSED_DIR, "analysis_results.json")) as f:
    analysis = json.load(f)

hypothesis_df = pd.DataFrame(analysis["testes_hipotese"])
summary_df = pd.DataFrame(analysis["estatisticas_descritivas"])

plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

print("Gerando graficos...")

# Figura 1: Boxplot tempo de resposta por complexidade e API
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=False)
for i, complexity in enumerate(COMPLEXITY_ORDER):
    ax = axes[i]
    subset = df[df["complexity"] == complexity]
    sns.boxplot(data=subset, x="api", y="response_time_ms", hue="api",
                palette=API_COLORS, ax=ax, width=0.5, legend=False)
    ax.set_title(f"Consulta {COMPLEXITY_LABELS[complexity]}")
    ax.set_xlabel("Tipo de API")
    ax.set_ylabel("Tempo de Resposta (ms)" if i == 0 else "")
    ax.grid(axis="y", alpha=0.3)
fig.suptitle("RQ1: Tempo de Resposta - REST vs GraphQL", fontsize=16, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_rq1_boxplot_tempo.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_rq1_boxplot_tempo.png")

# Figura 2: Boxplot tamanho da resposta por complexidade e API
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=False)
for i, complexity in enumerate(COMPLEXITY_ORDER):
    ax = axes[i]
    subset = df[df["complexity"] == complexity]
    sns.boxplot(data=subset, x="api", y="response_size_bytes", hue="api",
                palette=API_COLORS, ax=ax, width=0.5, legend=False)
    ax.set_title(f"Consulta {COMPLEXITY_LABELS[complexity]}")
    ax.set_xlabel("Tipo de API")
    ax.set_ylabel("Tamanho da Resposta (bytes)" if i == 0 else "")
    ax.grid(axis="y", alpha=0.3)
fig.suptitle("RQ2: Tamanho da Resposta - REST vs GraphQL", fontsize=16, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_rq2_boxplot_tamanho.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_rq2_boxplot_tamanho.png")

# Figura 3: Barras - mediana do tempo por API e complexidade
fig, ax = plt.subplots(figsize=(10, 6))
pivot_time = summary_df[summary_df["metrica"] == "tempo"].pivot_table(
    index="complexidade", columns="api", values="mediana"
).reindex(COMPLEXITY_ORDER)
x = np.arange(len(COMPLEXITY_ORDER))
width = 0.35
bars1 = ax.bar(x - width/2, pivot_time["REST"], width, label="REST", color=API_COLORS["REST"])
bars2 = ax.bar(x + width/2, pivot_time["GraphQL"], width, label="GraphQL", color=API_COLORS["GraphQL"])
ax.set_xlabel("Complexidade da Consulta")
ax.set_ylabel("Mediana do Tempo de Resposta (ms)")
ax.set_title("RQ1: Mediana do Tempo de Resposta por Complexidade")
ax.set_xticks(x)
ax.set_xticklabels([COMPLEXITY_LABELS[c] for c in COMPLEXITY_ORDER])
ax.legend()
ax.grid(axis="y", alpha=0.3)
for bar in bars1 + bars2:
    height = bar.get_height()
    ax.annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10)
fig.savefig(os.path.join(OUTPUT_DIR, "fig_rq1_barras_mediana_tempo.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_rq1_barras_mediana_tempo.png")

# Figura 4: Barras - mediana do tamanho por API e complexidade
fig, ax = plt.subplots(figsize=(10, 6))
pivot_size = summary_df[summary_df["metrica"] == "tamanho"].pivot_table(
    index="complexidade", columns="api", values="mediana"
).reindex(COMPLEXITY_ORDER)
x = np.arange(len(COMPLEXITY_ORDER))
bars1 = ax.bar(x - width/2, pivot_size["REST"], width, label="REST", color=API_COLORS["REST"])
bars2 = ax.bar(x + width/2, pivot_size["GraphQL"], width, label="GraphQL", color=API_COLORS["GraphQL"])
ax.set_xlabel("Complexidade da Consulta")
ax.set_ylabel("Mediana do Tamanho da Resposta (bytes)")
ax.set_title("RQ2: Mediana do Tamanho da Resposta por Complexidade")
ax.set_xticks(x)
ax.set_xticklabels([COMPLEXITY_LABELS[c] for c in COMPLEXITY_ORDER])
ax.legend()
ax.grid(axis="y", alpha=0.3)
for bar in bars1 + bars2:
    height = bar.get_height()
    ax.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10)
fig.savefig(os.path.join(OUTPUT_DIR, "fig_rq2_barras_mediana_tamanho.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_rq2_barras_mediana_tamanho.png")

# Figura 5: Tabela resumo de resultados estatisticos
fig, ax = plt.subplots(figsize=(14, 4))
ax.axis("off")

table_data = []
for _, row in hypothesis_df.iterrows():
    rq = row["RQ"]
    comp = COMPLEXITY_LABELS[row["complexidade"]]
    rest_m = row["rest_mediana"]
    gql_m = row["graphql_mediana"]
    diff = row["diferenca_mediana_pct"]
    pval = row["p_valor"]
    sig = row["significativo"]
    dir_txt = row["direcao"]

    if rq == "RQ1":
        unit_rest = f"{rest_m:.2f} ms"
        unit_gql = f"{gql_m:.2f} ms"
        unit_diff = f"{diff:+.1f}%"
    else:
        unit_rest = f"{int(rest_m)} bytes"
        unit_gql = f"{int(gql_m)} bytes"
        unit_diff = f"{diff:+.1f}%"

    table_data.append([rq, comp, unit_rest, unit_gql, unit_diff, pval, sig, dir_txt])

col_labels = ["RQ", "Complexidade", "REST\n(mediana)", "GraphQL\n(mediana)", "Diferenca\n(%)", "p-valor", "Significativo?", "Direcao"]
table = ax.table(cellText=table_data, colLabels=col_labels, loc="center", cellLoc="center")
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.1, 1.6)

for i, row_data in enumerate(table_data):
    sig_idx = 6
    if row_data[sig_idx] == "Sim":
        table[i + 1, sig_idx].set_facecolor("#C8E6C9")
    else:
        table[i + 1, sig_idx].set_facecolor("#FFCDD2")

for j in range(len(col_labels)):
    table[0, j].set_facecolor("#1976D2")
    table[0, j].set_text_props(color="white", fontweight="bold")

fig.suptitle("Resumo dos Testes Mann-Whitney U (alfa = 0.05)", fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_heatmap_pvalores.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_heatmap_pvalores.png (tabela resumo)")

# Figura 6: Comparacao de medianas REST vs GraphQL
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, (metric, title, unit) in enumerate([
    ("tempo", "Tempo de Resposta", "ms"),
    ("tamanho", "Tamanho da Resposta", "bytes")
]):
    ax = axes[idx]
    sub = summary_df[summary_df["metrica"] == metric]
    rest_vals = [sub[(sub["complexidade"] == c) & (sub["api"] == "REST")]["mediana"].values[0] for c in COMPLEXITY_ORDER]
    gql_vals = [sub[(sub["complexidade"] == c) & (sub["api"] == "GraphQL")]["mediana"].values[0] for c in COMPLEXITY_ORDER]

    x = np.arange(len(COMPLEXITY_ORDER))
    width = 0.35
    ax.bar(x - width/2, rest_vals, width, label="REST", color=API_COLORS["REST"])
    ax.bar(x + width/2, gql_vals, width, label="GraphQL", color=API_COLORS["GraphQL"])
    ax.set_xlabel("Complexidade da Consulta")
    ax.set_ylabel(f"Mediana ({unit})")
    ax.set_title(f"{title} - Medianas")
    ax.set_xticks(x)
    ax.set_xticklabels([COMPLEXITY_LABELS[c] for c in COMPLEXITY_ORDER])
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

fig.suptitle("Comparacao de Medianas: REST vs GraphQL", fontsize=14, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_comparacao_medianas.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_comparacao_medianas.png")

# Figura 7: Distribuicao (violin plot)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, (metric, title, col, unit) in enumerate([
    ("tempo", "RQ1: Tempo de Resposta", "response_time_ms", "ms"),
    ("tamanho", "RQ2: Tamanho da Resposta", "response_size_bytes", "bytes"),
]):
    ax = axes[idx]
    sns.violinplot(data=df, x="complexity", y=col, hue="api",
                   palette=API_COLORS, ax=ax, order=COMPLEXITY_ORDER, inner="box")
    ax.set_title(title)
    ax.set_xlabel("Complexidade da Consulta")
    ax.set_ylabel(f"{title.split(': ')[1]} ({unit})")
    ax.legend(title="API")

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_violin_distribuicao.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_violin_distribuicao.png")

# Figura 8: Diferenca percentual
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, rq in enumerate(["RQ1", "RQ2"]):
    ax = axes[idx]
    sub = hypothesis_df[hypothesis_df["RQ"] == rq].copy()
    complexities = sub["complexidade"].values
    diffs = sub["diferenca_mediana_pct"].values.astype(float)

    colors = ["#27AE60" if d < 0 else "#E74C3C" for d in diffs]
    ax.bar(range(len(complexities)), diffs, color=colors, width=0.6)
    ax.set_xticks(range(len(complexities)))
    ax.set_xticklabels([COMPLEXITY_LABELS[c] for c in complexities])
    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_xlabel("Complexidade da Consulta")
    ax.set_ylabel("Diferenca Percentual (%)")
    title = "RQ1: Tempo" if rq == "RQ1" else "RQ2: Tamanho"
    ax.set_title(f"{title} - Diferenca GraphQL vs REST (%)")
    ax.grid(axis="y", alpha=0.3)

    for i, d in enumerate(diffs):
        ax.annotate(f"{d:+.1f}%", xy=(i, d), xytext=(0, 5 if d > 0 else -15),
                    textcoords="offset points", ha="center", fontsize=10, fontweight="bold")

fig.suptitle("Diferenca Percentual (GraphQL em relacao ao REST)", fontsize=14, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_diferenca_percentual.png"), bbox_inches="tight")
plt.close(fig)
print("  fig_diferenca_percentual.png")

resumo_rq1 = hypothesis_df[hypothesis_df["RQ"] == "RQ1"][["complexidade", "rest_mediana", "graphql_mediana", "diferenca_mediana_pct", "p_valor", "significativo", "direcao"]].copy()
resumo_rq2 = hypothesis_df[hypothesis_df["RQ"] == "RQ2"][["complexidade", "rest_mediana", "graphql_mediana", "diferenca_mediana_pct", "p_valor", "significativo", "direcao"]].copy()

print("\n" + "=" * 70)
print("TABELA RESUMO RQ1 - Tempo de Resposta")
print("=" * 70)
print(resumo_rq1.to_string(index=False))

print("\n" + "=" * 70)
print("TABELA RESUMO RQ2 - Tamanho da Resposta")
print("=" * 70)
print(resumo_rq2.to_string(index=False))

print(f"\nTodos os graficos foram salvos em: {OUTPUT_DIR}")