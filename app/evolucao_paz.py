import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Evolução Global da Paz Viva", layout="wide")

st.title("📈 Evolução Global da Paz Viva")
st.markdown("Média mundial do Índice de Paz ao longo do tempo.")

DB_PATH = Path("data/database/paz.db")

# -------------------------------
# CONEXÃO COM O BANCO
# -------------------------------
conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    "SELECT year, month, indicator_value FROM country_metrics",
    conn
)

conn.close()

# -------------------------------
# AGRUPAR POR MÊS GLOBAL
# -------------------------------
df["ano_mes"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

df_global = df.groupby("ano_mes")["indicator_value"].mean().reset_index()

df_global.rename(columns={"indicator_value": "media_global"}, inplace=True)

# -------------------------------
# GRÁFICO
# -------------------------------
fig = px.line(
    df_global,
    x="ano_mes",
    y="media_global",
    title="🌍 Média Global do Índice de Paz Viva",
    markers=True
)

fig.update_layout(
    xaxis_title="Período",
    yaxis_title="Índice Médio Global",
    yaxis_range=[0, 100]
)

st.plotly_chart(fig, use_container_width=True)

st.success("✅ Gráfico de Evolução Global da Paz carregado com sucesso!")
