import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Ranking Global da Paz Viva", layout="wide")

st.title("🏆 Ranking Global da Paz Viva")
st.markdown("Classificação dos países pelo Índice Oficial da Paz Viva.")

DB_PATH = Path("data/database/paz.db")

# -------------------------------
# FUNÇÃO DA ESCALA OFICIAL
# -------------------------------
def classificar_paz(valor):
    if pd.isna(valor):
        return "Sem dados"
    if valor == 100:
        return "Excelente"
    elif 91 <= valor <= 99:
        return "Bom"
    elif 71 <= valor <= 90:
        return "Médio"
    elif 51 <= valor <= 70:
        return "Baixo"
    else:
        return "Crítico"

# -------------------------------
# CONEXÃO COM O BANCO
# -------------------------------
conn = sqlite3.connect(DB_PATH)

df_index = pd.read_sql_query(
    "SELECT country_code, year, month, indicator_value FROM country_metrics",
    conn
)

df_countries = pd.read_sql_query(
    "SELECT country_code, country_name FROM country_metadata",
    conn
)

conn.close()

# -------------------------------
# FILTRO DE DATA
# -------------------------------
st.sidebar.header("📅 Filtro de Tempo")

anos = sorted(df_index["year"].unique())
meses = sorted(df_index["month"].unique())

ano_sel = st.sidebar.selectbox("Ano", anos)
mes_sel = st.sidebar.selectbox("Mês", meses)

df_filtrado = df_index[
    (df_index["year"] == ano_sel) &
    (df_index["month"] == mes_sel)
]

df_rank = df_filtrado.merge(
    df_countries,
    on="country_code",
    how="left"
)

df_rank["nivel_paz"] = df_rank["indicator_value"].apply(classificar_paz)

# -------------------------------
# ORDENAÇÃO DO RANKING
# -------------------------------
df_rank = df_rank.sort_values(by="indicator_value", ascending=False)

df_rank["Posição"] = range(1, len(df_rank) + 1)

# -------------------------------
# DESTAQUES
# -------------------------------
st.subheader("🌟 Top 10 Países com Maior Índice de Paz Viva")

st.dataframe(
    df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]].head(10),
    use_container_width=True
)

st.divider()

st.subheader("🚨 Países em Nível Crítico")

df_critico = df_rank[df_rank["nivel_paz"] == "Crítico"]

st.dataframe(
    df_critico[["country_name", "indicator_value"]],
    use_container_width=True
)

st.divider()

st.subheader("📊 Ranking Completo")

st.dataframe(
    df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]],
    use_container_width=True
)

st.success("✅ Ranking Global da Paz Viva carregado com sucesso!")
