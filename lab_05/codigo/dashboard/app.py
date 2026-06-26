import streamlit as st
import pandas as pd
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "dados")
RESULTS_CSV = os.path.join(DATA_DIR, "raw", "resultados.csv")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

st.set_page_config(page_title="GraphQL vs REST - Dashboard", layout="wide")
st.title("GraphQL vs REST - Dashboard de Resultados")

df = pd.read_csv(RESULTS_CSV)
df = df[df["response_time_ms"] > 0].copy()

with open(os.path.join(PROCESSED_DIR, "analysis_results.json")) as f:
    analysis = json.load(f)

summary_df = pd.DataFrame(analysis["estatisticas_descritivas"])
hypothesis_df = pd.DataFrame(analysis["testes_hipotese"])
normality_df = pd.DataFrame(analysis["teste_normalidade"])

st.sidebar.header("Navegacao")
page = st.sidebar.radio("Secao:", [
    "Resumo Geral",
    "RQ1 - Tempo de Resposta",
    "RQ2 - Tamanho da Resposta",
    "Testes Estatisticos",
    "Dados Brutos"
])

if page == "Resumo Geral":
    st.header("Resumo Geral do Experimento")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Medicoes", len(df))
    col2.metric("Tipos de Consulta", df["query_name"].nunique())
    col3.metric("Repeticoes por Consulta", df["repetition"].max())

    st.subheader("Estatisticas Descritivas")
    st.dataframe(summary_df, width="stretch")

    st.subheader("Comparacao de Medianas")
    st.image(os.path.join(PROCESSED_DIR, "fig_comparacao_medianas.png"))

    st.subheader("Diferenca Percentual")
    st.image(os.path.join(PROCESSED_DIR, "fig_diferenca_percentual.png"))

elif page == "RQ1 - Tempo de Resposta":
    st.header("RQ1: Respostas as consultas GraphQL sao mais rapidas que REST?")

    st.subheader("Resultado: NAO - REST e mais rapido em todas as complexidades")
    st.markdown("""
    As consultas REST apresentaram tempo de resposta significativamente menor que GraphQL
    em todos os niveis de complexidade (p < 0.001, teste Mann-Whitney U).
    """)

    st.subheader("Boxplot - Tempo de Resposta")
    st.image(os.path.join(PROCESSED_DIR, "fig_rq1_boxplot_tempo.png"))

    st.subheader("Mediana do Tempo de Resposta por Complexidade")
    st.image(os.path.join(PROCESSED_DIR, "fig_rq1_barras_mediana_tempo.png"))

    st.subheader("Distribuicao (Violin Plot)")
    st.image(os.path.join(PROCESSED_DIR, "fig_violin_distribuicao.png"))

    st.subheader("Detalhes RQ1")
    rq1 = hypothesis_df[hypothesis_df["RQ"] == "RQ1"]
    st.dataframe(rq1[["complexidade", "rest_mediana", "graphql_mediana",
                       "diferenca_mediana_pct", "p_valor", "significativo", "direcao"]])

elif page == "RQ2 - Tamanho da Resposta":
    st.header("RQ2: Respostas GraphQL tem tamanho menor que REST?")

    st.subheader("Resultado: SIM - GraphQL retorna respostas menores em todas as complexidades")
    st.markdown("""
    As respostas GraphQL foram significativamente menores que REST
    em todos os niveis de complexidade (p < 0.001, teste Mann-Whitney U).
    """)

    st.subheader("Boxplot - Tamanho da Resposta")
    st.image(os.path.join(PROCESSED_DIR, "fig_rq2_boxplot_tamanho.png"))

    st.subheader("Mediana do Tamanho da Resposta por Complexidade")
    st.image(os.path.join(PROCESSED_DIR, "fig_rq2_barras_mediana_tamanho.png"))

    st.subheader("Detalhes RQ2")
    rq2 = hypothesis_df[hypothesis_df["RQ"] == "RQ2"]
    st.dataframe(rq2[["complexidade", "rest_mediana", "graphql_mediana",
                       "diferenca_mediana_pct", "p_valor", "significativo", "direcao"]])

elif page == "Testes Estatisticos":
    st.header("Testes Estatisticos")

    st.subheader("Teste de Normalidade (Shapiro-Wilk)")
    st.dataframe(normality_df, width="stretch")

    st.subheader("Testes de Hipotese (Mann-Whitney U)")
    st.dataframe(hypothesis_df, width="stretch")

    st.subheader("Heatmap de p-valores")
    st.image(os.path.join(PROCESSED_DIR, "fig_heatmap_pvalores.png"))

elif page == "Dados Brutos":
    st.header("Dados Brutos do Experimento")
    st.dataframe(df, width="stretch")

    st.download_button(
        "Baixar CSV",
        df.to_csv(index=False),
        "resultados_experimento.csv",
        "text/csv"
    )