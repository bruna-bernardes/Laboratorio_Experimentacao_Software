import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "dados", "processed")
GRAFICOS_DIR = os.path.join(PROJECT_ROOT, "graficos")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

with open(os.path.join(DATA_DIR, "dataset_stats.json")) as f:
    stats = json.load(f)

df = pd.read_csv(os.path.join(DATA_DIR, "prs_processed.csv"))

print(f"Dataset carregado: {len(df):,} PRs")

plt.rcParams.update({
    "figure.figsize": (12, 7),
    "figure.dpi": 150,
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

COLORS = {"Merged": "#2ecc71", "Closed": "#e74c3c", "Open": "#3498db", "Abandonada": "#e74c3c", "Nao abandonada": "#2ecc71"}

# Fig 1: Distribuicao dos PRs por estado
fig, ax = plt.subplots()
state_counts = df["state_label"].value_counts()
colors = [COLORS.get(s, "#95a5a6") for s in state_counts.index]
wedges, texts, autotexts = ax.pie(
    state_counts.values, labels=state_counts.index, autopct="%1.1f%%",
    colors=colors, startangle=90, textprops={"fontsize": 13}
)
for t in autotexts:
    t.set_fontweight("bold")
ax.set_title(f"Distribuicao dos PRs por Estado\n(n = {len(df):,})")
fig.savefig(os.path.join(GRAFICOS_DIR, "fig01_distribuicao_estados.png"), bbox_inches="tight")
plt.close(fig)
print("fig01_distribuicao_estados.png")

# Fig 2: KPI - Taxa de abandono global
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis("off")
rate = stats["abandonment_rate"]
ax.text(0.5, 0.7, f"{rate}%", fontsize=72, ha="center", va="center", fontweight="bold", color="#e74c3c")
ax.text(0.5, 0.35, "Taxa de Abandono Global", fontsize=20, ha="center", va="center")
ax.text(0.5, 0.15, f"{stats['abandoned']:,} abandonadas de {stats['total_prs']:,} PRs", fontsize=14, ha="center", va="center", color="gray")
fig.savefig(os.path.join(GRAFICOS_DIR, "fig02_taxa_abandono.png"), bbox_inches="tight")
plt.close(fig)
print("fig02_taxa_abandono.png")

# Fig 3: Top 10 repos por numero de PRs
repo_stats = pd.read_csv(os.path.join(DATA_DIR, "repo_stats.csv"))
top10 = repo_stats.nlargest(10, "total")
fig, ax = plt.subplots()
bars = ax.barh(top10["repo"], top10["total"], color="#3498db")
ax.set_xlabel("Numero de PRs")
ax.set_title("Top 10 Repositorios por Numero de PRs")
ax.invert_yaxis()
for bar in bars:
    width = bar.get_width()
    ax.text(width + 200, bar.get_y() + bar.get_height()/2, f"{int(width):,}", va="center", fontsize=10)
fig.savefig(os.path.join(GRAFICOS_DIR, "fig03_top10_repos_prs.png"), bbox_inches="tight")
plt.close(fig)
print("fig03_top10_repos_prs.png")

# Fig 4: Top 5 maior e menor taxa de abandono
top5_high = repo_stats.nlargest(5, "abandonment_rate")
top5_low = repo_stats[repo_stats["total"] >= 100].nsmallest(5, "abandonment_rate")
combined = pd.concat([top5_high, top5_low])
combined["label"] = combined["repo"] + " (" + combined["total"].astype(str) + " PRs)"
fig, ax = plt.subplots()
colors_bar = ["#e74c3c"] * 5 + ["#2ecc71"] * 5
bars = ax.barh(range(len(combined)), combined["abandonment_rate"], color=colors_bar)
ax.set_yticks(range(len(combined)))
ax.set_yticklabels(combined["label"])
ax.set_xlabel("Taxa de Abandono (%)")
ax.set_title("Top 5 Maior e Menor Taxa de Abandono\n(repos com 100+ PRs para menor)")
ax.invert_yaxis()
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", va="center", fontsize=10)
fig.savefig(os.path.join(GRAFICOS_DIR, "fig04_taxa_abandono_repos.png"), bbox_inches="tight")
plt.close(fig)
print("fig04_taxa_abandono_repos.png")

# Fig 5: Distribuicao do tempo ate primeira resposta
valid_time = df[df["time_to_first_response_h"].notna()]
fig, ax = plt.subplots()
ax.hist(valid_time["time_to_first_response_h"], bins=100, range=(0, 500), color="#3498db", edgecolor="white", alpha=0.8)
median_val = valid_time["time_to_first_response_h"].median()
mean_val = valid_time["time_to_first_response_h"].mean()
ax.axvline(median_val, color="#e74c3c", linestyle="--", linewidth=2, label=f"Mediana: {median_val:.1f}h")
ax.axvline(mean_val, color="#f39c12", linestyle="--", linewidth=2, label=f"Media: {mean_val:.1f}h")
ax.set_xlabel("Tempo ate a Primeira Resposta (horas)")
ax.set_ylabel("Numero de PRs")
ax.set_title("Distribuicao do Tempo ate a Primeira Resposta\n(limitado a 500h)")
ax.legend()
fig.savefig(os.path.join(GRAFICOS_DIR, "fig05_tempo_primeira_resposta.png"), bbox_inches="tight")
plt.close(fig)
print("fig05_tempo_primeira_resposta.png")

# Fig 6: Distribuicao de participantes por PR
fig, ax = plt.subplots()
p_counts = df["participants_count"].value_counts().sort_index().head(20)
ax.bar(p_counts.index, p_counts.values, color="#3498db", edgecolor="white")
ax.set_xlabel("Numero de Participantes")
ax.set_ylabel("Numero de PRs")
ax.set_title("Distribuicao do Numero de Participantes por PR\n(0-20 participantes)")
fig.savefig(os.path.join(GRAFICOS_DIR, "fig06_participantes_distribuicao.png"), bbox_inches="tight")
plt.close(fig)
print("fig06_participantes_distribuicao.png")

# Fig 7: Distribuicao de tamanho (linhas alteradas)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, col, title in [
    (axes[0], "total_lines", "Linhas Alteradas"),
    (axes[1], "changed_files", "Arquivos Modificados"),
    (axes[2], "commits", "Commits"),
]:
    data = df[df[col] < df[col].quantile(0.95)]
    ax.hist(data[col], bins=80, color="#3498db", edgecolor="white", alpha=0.8)
    med = df[col].median()
    ax.axvline(med, color="#e74c3c", linestyle="--", linewidth=2, label=f"Mediana: {med:.0f}")
    ax.set_xlabel(title)
    ax.set_ylabel("Numero de PRs")
    ax.set_title(f"Distribuicao de {title}")
    ax.legend(fontsize=9)
fig.suptitle("Caracterizacao do Tamanho dos PRs (percentil 95)", fontsize=14, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(GRAFICOS_DIR, "fig07_tamanho_distribuicao.png"), bbox_inches="tight")
plt.close(fig)
print("fig07_tamanho_distribuicao.png")

# Tabela: Caracterizacao dos subgrupos abandonadas vs nao abandonadas
ab = df[df["abandoned"] == 1]
nab = df[df["abandoned"] == 0]

comparison = pd.DataFrame({
    "Metrica": [
        "Numero de PRs",
        "Mediana participantes",
        "Media participantes",
        "Mediana tempo ate 1a resposta (h)",
        "Media tempo ate 1a resposta (h)",
        "Mediana linhas alteradas",
        "Media linhas alteradas",
        "Mediana arquivos modificados",
        "Media arquivos modificados",
        "Mediana commits",
        "Media commits",
    ],
    "Abandonadas": [
        f"{len(ab):,}",
        f"{ab['participants_count'].median():.2f}",
        f"{ab['participants_count'].mean():.2f}",
        f"{ab['time_to_first_response_h'].median():.2f}",
        f"{ab['time_to_first_response_h'].mean():.2f}",
        f"{ab['total_lines'].median():.0f}",
        f"{ab['total_lines'].mean():.2f}",
        f"{ab['changed_files'].median():.0f}",
        f"{ab['changed_files'].mean():.2f}",
        f"{ab['commits'].median():.0f}",
        f"{ab['commits'].mean():.2f}",
    ],
    "Nao abandonadas": [
        f"{len(nab):,}",
        f"{nab['participants_count'].median():.2f}",
        f"{nab['participants_count'].mean():.2f}",
        f"{nab['time_to_first_response_h'].median():.2f}",
        f"{nab['time_to_first_response_h'].mean():.2f}",
        f"{nab['total_lines'].median():.0f}",
        f"{nab['total_lines'].mean():.2f}",
        f"{nab['changed_files'].median():.0f}",
        f"{nab['changed_files'].mean():.2f}",
        f"{nab['commits'].median():.0f}",
        f"{nab['commits'].mean():.2f}",
    ],
})

comparison.to_markdown(os.path.join(DATA_DIR, "comparacao_abandonadas.md"), index=False)
comparison.to_csv(os.path.join(DATA_DIR, "comparacao_abandonadas.csv"), index=False)
print("\nComparacao abandonadas vs nao abandonadas:")
print(comparison.to_string(index=False))

print(f"\nGraficos salvos em: {GRAFICOS_DIR}")