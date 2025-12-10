import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Relatório Mensal da Paz Viva", layout="wide")

st.title("📄 Relatório Mensal da Paz Viva")

st.markdown("""
Este relatório apresenta a **situação global da Paz Viva** para o período selecionado,
com base no Índice Oficial da Paz Viva e nos Sóis do Movimento da Paz.
""")

DB_PATH = Path("data/database/paz.db")

# -------------------------------
# ESCALA OFICIAL
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

df_suns = pd.read_sql_query(
    "SELECT country_code, created_at FROM peacekeepers",
    conn
)

conn.close()

df_suns["created_at"] = pd.to_datetime(df_suns["created_at"])

# -------------------------------
# SELEÇÃO DE PERÍODO
# -------------------------------
st.sidebar.header("📅 Período do Relatório")

anos = sorted(df_index["year"].unique())
meses = sorted(df_index["month"].unique())

ano_sel = st.sidebar.selectbox("Ano", anos)
mes_sel = st.sidebar.selectbox("Mês", meses)

# Índices no período
df_mes = df_index[
    (df_index["year"] == ano_sel) &
    (df_index["month"] == mes_sel)
].copy()

df_mes = df_mes.merge(df_countries, on="country_code", how="left")

df_mes["nivel_paz"] = df_mes["indicator_value"].apply(classificar_paz)

# Sóis no período
df_suns_mes = df_suns[
    (df_suns["created_at"].dt.year == ano_sel) &
    (df_suns["created_at"].dt.month == mes_sel)
].copy()

total_suns_mes = len(df_suns_mes)
total_suns_global = len(df_suns)

# -------------------------------
# VISÃO GERAL
# -------------------------------
st.subheader("🌍 Visão Geral do Período")

col1, col2, col3, col4 = st.columns(4)

media_global = df_mes["indicator_value"].mean()
num_paises = df_mes["country_code"].nunique()

col1.metric("Índice Médio Global", f"{media_global:.1f}" if pd.notna(media_global) else "-")
col2.metric("Países com dados no período", num_paises)
col3.metric("Sóis da Paz neste mês", total_suns_mes)
col4.metric("Sóis acumulados (global)", total_suns_global)

st.markdown("---")

# -------------------------------
# DESTAQUES
# -------------------------------
st.subheader("🏆 Destaques do Mês")

df_mes_ord = df_mes.sort_values(by="indicator_value", ascending=False)

top5 = df_mes_ord.head(5)
bottom5 = df_mes_ord.tail(5)

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.markdown("### 🌟 Top 5 Países com maior Índice")
    if not top5.empty:
        st.table(
            top5[["country_name", "indicator_value", "nivel_paz"]].reset_index(drop=True)
        )
    else:
        st.info("Sem dados para este período.")

with col_t2:
    st.markdown("### ⚠️ 5 Países em situação mais crítica")
    if not bottom5.empty:
        st.table(
            bottom5[["country_name", "indicator_value", "nivel_paz"]].reset_index(drop=True)
        )
    else:
        st.info("Sem dados para este período.")

st.markdown("---")

# -------------------------------
# DISTRIBUIÇÃO POR NÍVEL
# -------------------------------
st.subheader("📊 Distribuição dos Países por Nível de Paz")

df_dist = (
    df_mes.groupby("nivel_paz")
    .size()
    .reset_index(name="quantidade")
    .sort_values(by="quantidade", ascending=False)
)

if not df_dist.empty:
    st.dataframe(df_dist, use_container_width=True)
else:
    st.info("Sem dados de países para este período.")

st.markdown("---")

# -------------------------------
# TABELA COMPLETA
# -------------------------------
st.subheader("📋 Tabela Oficial do Índice por País (Período Selecionado)")

if not df_mes.empty:
    df_tabela = df_mes[["country_name", "indicator_value", "nivel_paz"]].copy()
    df_tabela = df_tabela.sort_values(by="indicator_value", ascending=False)
    df_tabela.rename(columns={
        "country_name": "País",
        "indicator_value": "Índice de Paz",
        "nivel_paz": "Nível"
    }, inplace=True)
    st.dataframe(df_tabela, use_container_width=True, height=400)
else:
    st.info("Sem dados de índice de paz para este período.")

st.markdown("---")

st.markdown("""
### 📌 Como gerar o PDF deste relatório

1. Com o relatório aberto na tela, pressione **Ctrl + P** (no Windows) ou **Cmd + P** (no Mac).
2. Em **Destino/Impressora**, escolha **“Salvar como PDF”**.
3. Ajuste a orientação (retrato ou paisagem) se desejar.
4. Clique em **Salvar**.

Assim você obtém um **Relatório Oficial da Paz Viva** pronto para:
- compartilhar com grupos,
- apresentar em encontros,
- enviar para instituições, imprensa, órgãos públicos.
""")

st.success("✅ Relatório Mensal da Paz Viva pronto para impressão ou exportação em PDF.")
