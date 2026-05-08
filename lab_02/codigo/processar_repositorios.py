import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy.stats import spearmanr

# Carrega o CSV
df = pd.read_csv(
    'lab02/dados/metricas_1000repos.csv'
)

# Diretório para salvar os gráficos
output_dir = 'lab_02/relatorios/graficos'

os.makedirs(output_dir, exist_ok=True)

quality_metrics = [
    'quality_cbo_mean', 'quality_dit_mean', 'quality_lcom_mean'
]
process_metrics = {
    'Popularidade (stars)': 'popularity_stars',
    'Maturidade (anos)': 'maturity_years',
    'Atividade (releases)': 'activity_releases',
    'Tamanho (LOC)': 'size_loc',
    'Tamanho (comentários)': 'size_comments_loc'
}

def plot_relation(x_metric, y_metric, xlabel, ylabel, title, filename):
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x=x_metric, y=y_metric)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

def correlation_report(x_metric, y_metric):
    pearson = df[x_metric].corr(df[y_metric])
    spearman, _ = spearmanr(df[x_metric], df[y_metric])
    return pearson, spearman

# RQ01: Popularidade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Popularidade (stars)'], qm,
        'Popularidade (stars)', qm,
        f'Popularidade vs {qm}',
        f'popularidade_vs_{qm}.png'
    )
    pearson, spearman = correlation_report(process_metrics['Popularidade (stars)'], qm)
    print(f"Correlação entre Popularidade e {qm}: Pearson={pearson:.3f} | Spearman={spearman:.3f}")

# RQ02: Maturidade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Maturidade (anos)'], qm,
        'Maturidade (anos)', qm,
        f'Maturidade vs {qm}',
        f'maturidade_vs_{qm}.png'
    )
    pearson, spearman = correlation_report(process_metrics['Maturidade (anos)'], qm)
    print(f"Correlação entre Maturidade e {qm}: Pearson={pearson:.3f} | Spearman={spearman:.3f}")

# RQ03: Atividade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Atividade (releases)'], qm,
        'Atividade (releases)', qm,
        f'Atividade vs {qm}',
        f'atividade_vs_{qm}.png'
    )
    pearson, spearman = correlation_report(process_metrics['Atividade (releases)'], qm)
    print(f"Correlação entre Atividade e {qm}: Pearson={pearson:.3f} | Spearman={spearman:.3f}")

# RQ04: Tamanho vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Tamanho (LOC)'], qm,
        'Tamanho (LOC)', qm,
        f'Tamanho LOC vs {qm}',
        f'tamanho_loc_vs_{qm}.png'
    )
    pearson, spearman = correlation_report(process_metrics['Tamanho (LOC)'], qm)
    print(f"Correlação entre Tamanho LOC e {qm}: Pearson={pearson:.3f} | Spearman={spearman:.3f}")

    plot_relation(
        process_metrics['Tamanho (comentários)'], qm,
        'Tamanho (comentários)', qm,
        f'Tamanho Comentários vs {qm}',
        f'tamanho_comentarios_vs_{qm}.png'
    )
    pearson, spearman = correlation_report(process_metrics['Tamanho (comentários)'], qm)
    print(f"Correlação entre Tamanho Comentários e {qm}: Pearson={pearson:.3f} | Spearman={spearman:.3f}")

# Gerar resumo das métricas e salvar em summary.md
summary_path = 'lab02/relatorios/summary.md'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("# Resumo das Métricas dos Repositórios Java\n\n")
    f.write("## Estatísticas Gerais\n\n")
    f.write("| Métrica                 | Média      | Mediana    | Desvio Padrão | Mínimo   | Máximo   |\n")
    f.write("|-------------------------|------------|------------|---------------|----------|----------|\n")
    for col, label in [
        ('popularity_stars', 'Popularidade (stars)'),
        ('maturity_years', 'Maturidade (anos)'),
        ('activity_releases', 'Atividade (releases)'),
        ('size_loc', 'Tamanho (LOC)'),
        ('size_comments_loc', 'Tamanho (comentários)'),
        ('quality_cbo_mean', 'CBO (médio)'),
        ('quality_dit_mean', 'DIT (médio)'),
        ('quality_lcom_mean', 'LCOM (médio)')
    ]:
        f.write(f"| {label:23} | {df[col].mean():.2f} | {df[col].median():.2f} | {df[col].std():.2f} | {df[col].min():.2f} | {df[col].max():.2f} |\n")
    f.write("\n---\n")
