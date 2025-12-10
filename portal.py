import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path


# =====================================================
# FUNÇÃO: RANKING GLOBAL DA PAZ VIVA
# =====================================================

def mostrar_ranking():
    DB_PATH = Path(__file__).parent / "paz.db"

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

    conn = sqlite3.connect(DB_PATH)

    df_countries = pd.read_sql_query(
        "SELECT country_code, country_name FROM country_metadata",
        conn
    )

    df_index = pd.read_sql_query(
        "SELECT country_code, year, month, indicator_value FROM country_metrics",
        conn
    )

    conn.close()

    st.title("🏆 Ranking Global da Paz Viva")

    anos = sorted(df_index["year"].unique())
    meses = sorted(df_index["month"].unique())

    ano_sel = st.selectbox("Ano", anos)
    mes_sel = st.selectbox("Mês", meses)

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
    df_rank = df_rank.sort_values(by="indicator_value", ascending=False)
    df_rank["Posição"] = range(1, len(df_rank) + 1)

    st.subheader("🌟 Top 10 Países")
    st.dataframe(
        df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]].head(10),
        use_container_width=True
    )

    st.subheader("📊 Ranking Completo")
    st.dataframe(
        df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]],
        use_container_width=True
    )

    st.success("✅ Ranking carregado com sucesso.")


# =====================================================
# FUNÇÃO: RELATÓRIO MENSAL DA PAZ VIVA
# =====================================================

def mostrar_relatorio_mensal():
    DB_PATH = Path(__file__).parent / "paz.db"

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

    conn = sqlite3.connect(DB_PATH)

    df_index = pd.read_sql_query(
        "SELECT country_code, year, month, indicator_value FROM country_metrics",
        conn
    )

    df_countries = pd.read_sql_query(
        "SELECT country_code, country_name FROM country_metadata",
        conn
    )

    df_peacekeepers = pd.read_sql_query(
        "SELECT country_code, created_at FROM peacekeepers",
        conn
    )

    conn.close()

    df_peacekeepers["created_at"] = pd.to_datetime(df_peacekeepers["created_at"])

    st.title("📄 Relatório Mensal da Paz Viva")

    anos = sorted(df_index["year"].unique())
    meses = sorted(df_index["month"].unique())

    ano_sel = st.selectbox("Ano", anos)
    mes_sel = st.selectbox("Mês", meses)

    df_mes = df_index[
        (df_index["year"] == ano_sel) &
        (df_index["month"] == mes_sel)
    ].copy()

    df_mes = df_mes.merge(
        df_countries,
        on="country_code",
        how="left"
    )

    df_mes["nivel_paz"] = df_mes["indicator_value"].apply(classificar_paz)

    df_suns_mes = df_peacekeepers[
        (df_peacekeepers["created_at"].dt.year == ano_sel) &
        (df_peacekeepers["created_at"].dt.month == mes_sel)
    ]

    total_suns_mes = len(df_suns_mes)
    total_suns_global = len(df_peacekeepers)

    st.subheader("🌍 Visão Geral do Período")

    col1, col2, col3 = st.columns(3)

    media_global = df_mes["indicator_value"].mean()
    num_paises = df_mes["country_code"].nunique()

    col1.metric("Índice Médio Global", f"{media_global:.1f}" if pd.notna(media_global) else "-")
    col2.metric("Países com dados", num_paises)
    col3.metric("Sóis no período", total_suns_mes)

    st.markdown("---")

    st.subheader("🏆 Top 5 Países do Mês")

    top5 = df_mes.sort_values(by="indicator_value", ascending=False).head(5)
    st.dataframe(
        top5[["country_name", "indicator_value", "nivel_paz"]],
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("⚠️ Países em Nível Crítico")

    df_critico = df_mes[df_mes["nivel_paz"] == "Crítico"]
    st.dataframe(
        df_critico[["country_name", "indicator_value"]],
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("📊 Tabela Completa do Período")
    st.dataframe(
        df_mes[["country_name", "indicator_value", "nivel_paz"]],
        use_container_width=True
    )

    st.markdown("---")
    st.success("✅ Relatório mensal carregado com sucesso.")
