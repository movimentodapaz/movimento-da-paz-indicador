import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Contador Global de Sóis", layout="wide")

st.title("☀️ Contador Global de Sóis da Paz Viva")
st.markdown("Número de pacificadores do Movimento da Paz no planeta.")

DB_PATH = Path("data/database/paz.db")

# -------------------------------
# CONEXÃO COM O BANCO
# -------------------------------
conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    "SELECT country_code, created_at FROM peacekeepers",
    conn
)

df_countries = pd.read_sql_query(
    "SELECT country_code, country_name FROM country_metadata",
    conn
)

conn.close()

df["created_at"] = pd.to_datetime(df["created_at"])

# -------------------------------
# CONTADOR GLOBAL
# -------------------------------
total_suns = len(df)

st.metric("☀️ Total Global de Sóis da Paz", total_suns)

st.divider()

# -------------------------------
# CONTADOR POR PAÍS
# -------------------------------
df_country = df.groupby("country_code").size().reset_index(name="total")

df_country = df_country.merge(df_countries, on="country_code", how="left")

df_country = df_country.sort_values(by="total", ascending=False)

st.subheader("🌍 Sóis da Paz por País")
st.dataframe(df_country[["country_name", "total"]], use_container_width=True)

st.divider()

# -------------------------------
# CONTADOR POR MÊS
# -------------------------------
df["ano_mes"] = df["created_at"].dt.to_period("M").astype(str)

df_month = df.groupby("ano_mes").size().reset_index(name="total")

st.subheader("📅 Evolução Mensal dos Sóis da Paz")
st.dataframe(df_month, use_container_width=True)

st.success("✅ Contador Global de Sóis carregado com sucesso!")
