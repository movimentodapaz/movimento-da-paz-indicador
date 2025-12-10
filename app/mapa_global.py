import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px
import numpy as np

# ======================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================
st.set_page_config(page_title="Mapa Global da Paz Viva", layout="wide")

st.title("🌍 Mapa Global da Paz Viva")
st.markdown("Mapa com Índice de Paz por país, Sóis do Movimento da Paz e filtro por mês e ano.")

DB_PATH = Path("data/database/paz.db")

# ======================================
# FUNÇÃO DE CLASSIFICAÇÃO OFICIAL (SUA ESCALA)
# ======================================
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
    else:  # 0–50
        return "Crítico"

# ======================================
# CONEXÃO COM O BANCO
# ======================================
conn = sqlite3.connect(DB_PATH)

df_countries = pd.read_sql_query(
    "SELECT country_code, country_name, latitude, longitude FROM country_metadata",
    conn
)

df_peacekeepers = pd.read_sql_query(
    "SELECT country_code, latitude, longitude, created_at FROM peacekeepers",
    conn
)

df_index = pd.read_sql_query(
    "SELECT country_code, year, month, indicator_value FROM country_metrics",
    conn
)

conn.close()

# ======================================
# TRATAMENTO DE DATAS
# ======================================
df_peacekeepers["created_at"] = pd.to_datetime(df_peacekeepers["created_at"])

# ======================================
# FILTROS DE TEMPO
# ======================================
st.sidebar.header("📅 Filtro de Tempo")

anos_disponiveis = sorted(df_index["year"].unique())
meses_disponiveis = sorted(df_index["month"].unique())

ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis)
mes_selecionado = st.sidebar.selectbox("Mês", meses_disponiveis)

df_index_filtrado = df_index[
    (df_index["year"] == ano_selecionado) &
    (df_index["month"] == mes_selecionado)
]

df_mapa = df_countries.merge(
    df_index_filtrado,
    on="country_code",
    how="left"
)

# 👉 AQUI A ESCALA É REALMENTE APLICADA
df_mapa["nivel_paz"] = df_mapa["indicator_value"].apply(classificar_paz)

df_filtrado_suns = df_peacekeepers[
    (df_peacekeepers["created_at"].dt.year == ano_selecionado) &
    (df_peacekeepers["created_at"].dt.month == mes_selecionado)
]

st.sidebar.markdown(f"☀️ Sóis neste período: **{len(df_filtrado_suns)}**")

# ======================================
# FAIXAS DE COR BASEADAS NA SUA ESCALA
# ======================================
bins = [0, 50, 70, 90, 99, 100]
labels = ["Crítico", "Baixo", "Médio", "Bom", "Excelente"]

df_mapa["faixa_paz"] = pd.cut(
    df_mapa["indicator_value"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

color_map = {
    "Crítico": "red",
    "Baixo": "orange",
    "Médio": "yellow",
    "Bom": "lightgreen",
    "Excelente": "green"
}

df_mapa["cor_paz"] = df_mapa["faixa_paz"].map(color_map)

# ======================================
# MAPA COLORIDO PELA ESCALA OFICIAL
# ======================================
fig = px.scatter_geo(
    df_mapa,
    lat="latitude",
    lon="longitude",
    hover_name="country_name",
    color="faixa_paz",
    color_discrete_map=color_map,
    projection="natural earth",
    title="🌎 Índice Global da Paz Viva — Escala Oficial"
)

fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Índice: %{customdata[0]:.0f}<br>Nível: %{customdata[1]}",
    customdata=np.stack(
        (df_mapa["indicator_value"], df_mapa["nivel_paz"]),
        axis=-1
    )
)

# ======================================
# SÓIS DA PAZ
# ======================================
if not df_filtrado_suns.empty:
    fig_suns = px.scatter_geo(
        df_filtrado_suns,
        lat="latitude",
        lon="longitude",
        projection="natural earth",
        hover_name="country_code"
    )

    fig_suns.update_traces(
        marker=dict(
            size=14,
            color="gold",
            symbol="star",
            line=dict(width=1, color="orange")
        ),
        name="☀️ Sóis da Paz"
    )

    for trace in fig_suns.data:
        fig.add_trace(trace)

fig.update_layout(height=750)

st.plotly_chart(fig, use_container_width=True)

st.success("✅ Mapa global com Escala Oficial da Paz Viva aplicado com sucesso!")
