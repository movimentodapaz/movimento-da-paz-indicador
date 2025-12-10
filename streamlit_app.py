import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sqlite3
from pathlib import Path

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Indicador de Paz — Movimento da Paz", layout="wide")
st.title("Indicador de Paz — Movimento da Paz")

# =========================================================
# CAMINHO DO BANCO SQLITE (CORRETO PARA STREAMLIT CLOUD)
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "database" / "paz.db"

# =========================================================
# FUNÇÃO: CARREGAR DADOS AGREGADOS DE PAZ
# =========================================================
def load_aggregated(year, month):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT 
            c.country_code AS country_iso3,
            c.country_name,
            m.indicator_value AS peace_score_0_100
        FROM country_metrics m
        JOIN country_metadata c
          ON m.country_code = c.country_code
        WHERE m.year = ? AND m.month = ?
        """,
        conn,
        params=(year, month)
    )

    conn.close()
    return df

# =========================================================
# FUNÇÃO: CARREGAR DADOS DE "PACIFICADORES" (INSTAGRAM)
# =========================================================
def load_instagram(year, month):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT country_iso3, followers_count
        FROM instagram_followers
        WHERE year = ? AND month = ?
        """,
        conn,
        params=(year, month)
    )

    conn.close()
    return df

# =========================================================
# FILTROS LATERAIS
# =========================================================
col1, col2 = st.columns([3, 1])

with col2:
    st.header("Filtro")
    year = st.selectbox("Ano", options=list(range(2025, 2031)), index=0)
    month = st.selectbox("Mês", options=list(range(1, 13)), index=0)

# =========================================================
# MAPA GLOBAL DA PAZ
# =========================================================
st.subheader(f"Mapa Global — Paz ({year}-{month:02d})")

agg = load_aggregated(year, month)

if agg.empty:
    st.warning("Nenhum dado agregado encontrado para este período. Verifique a tabela country_metrics.")
else:
    fig = px.choropleth(
        agg,
        locations="country_iso3",
        color="peace_score_0_100",
        color_continuous_scale="Blues",
        range_color=(0, 100),
        hover_name="country_name",
        title="Índice Global da Paz (0–100)",
    )

    st.plotly_chart(fig, width="stretch")

# =========================================================
# MAPA DE PACIFICADORES (INSTAGRAM)
# =========================================================
st.subheader("Mapa de Pacificadores do Movimento da Paz")

try:
    ins_df = load_instagram(year, month)
except Exception as e:
    st.error("Tabela instagram_followers ainda não existe no banco.")
    st.stop()

if ins_df.empty:
    st.info("Nenhum dado de Instagram encontrado para este período.")
else:
    centroids_path = BASE_DIR / "data" / "external" / "country_centroids.csv"

    if centroids_path.exists():
        cdf = pd.read_csv(centroids_path)

        ins = ins_df.merge(cdf, left_on="country_iso3", right_on="iso3", how="left")
        ins = ins[ins["latitude"].notnull()]

        if not ins.empty:
            ins["size"] = (ins["followers_count"] / ins["followers_count"].max()) * 30 + 5

            fig2 = px.scatter_geo(
                ins,
                lat="latitude",
                lon="longitude",
                size="size",
                hover_name="country_iso3",
                projection="natural earth",
                title="Pacificadores — Cada ponto representa seguidores"
            )

            fig2.update_traces(
                marker=dict(color="goldenrod", opacity=0.9, line=dict(width=0))
            )

            st.plotly_chart(fig2, width="stretch")
        else:
            st.info("Não há coordenadas válidas para exibir os seguidores no mapa.")
    else:
        st.info("Adicione o arquivo: data/external/country_centroids.csv com colunas: iso3, latitude, longitude")
