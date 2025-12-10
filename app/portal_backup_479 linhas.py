import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px
import numpy as np

# ======================================
# CONFIG GERAL
# ======================================
st.set_page_config(page_title="Portal Global da Paz Viva", layout="wide")

DB_PATH = Path("data/database/paz.db")

# ======================================
# ESCALA OFICIAL
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
    else:
        return "Crítico"

# ======================================
# CARREGAR DADOS
# ======================================
@st.cache_data
def carregar_dados():
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

    df_peacekeepers["created_at"] = pd.to_datetime(df_peacekeepers["created_at"])

    return df_countries, df_peacekeepers, df_index

df_countries, df_peacekeepers, df_index = carregar_dados()

# ======================================
# MENU LATERAL
# ======================================
st.sidebar.title("🌐 Portal da Paz Viva")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Mapa Global",
        "Ranking Global",
        "Contador de Sóis",
        "Evolução Global da Paz",
        "Relatório Mensal"
    ]
)

# ======================================
# PÁGINA: MAPA GLOBAL
# ======================================
if pagina == "Mapa Global":
    st.title("🌍 Mapa Global da Paz Viva")
    st.markdown("Mapa com Índice de Paz por país, Sóis do Movimento da Paz e filtro por mês e ano.")

    st.sidebar.subheader("📅 Filtro de Tempo (Mapa)")

    anos_disponiveis = sorted(df_index["year"].unique())
    meses_disponiveis = sorted(df_index["month"].unique())

    ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, key="map_ano")
    mes_selecionado = st.sidebar.selectbox("Mês", meses_disponiveis, key="map_mes")

    df_index_filtrado = df_index[
        (df_index["year"] == ano_selecionado) &
        (df_index["month"] == mes_selecionado)
    ]

    df_mapa = df_countries.merge(
        df_index_filtrado,
        on="country_code",
        how="left"
    )

    df_mapa["nivel_paz"] = df_mapa["indicator_value"].apply(classificar_paz)

    # Faixas pela escala oficial
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

    df_suns_periodo = df_peacekeepers[
        (df_peacekeepers["created_at"].dt.year == ano_selecionado) &
        (df_peacekeepers["created_at"].dt.month == mes_selecionado)
    ]

    st.sidebar.markdown(f"☀️ Sóis neste período: **{len(df_suns_periodo)}**")

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

    if not df_suns_periodo.empty:
        fig_suns = px.scatter_geo(
            df_suns_periodo,
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
    st.success("✅ Mapa carregado com sucesso.")

# ======================================
# PÁGINA: RANKING GLOBAL
# ======================================
elif pagina == "Ranking Global":
    st.title("🏆 Ranking Global da Paz Viva")

    st.sidebar.subheader("📅 Filtro de Tempo (Ranking)")

    anos = sorted(df_index["year"].unique())
    meses = sorted(df_index["month"].unique())

    ano_sel = st.sidebar.selectbox("Ano", anos, key="rank_ano")
    mes_sel = st.sidebar.selectbox("Mês", meses, key="rank_mes")

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

    st.subheader("🌟 Top 10 Países com maior Índice de Paz Viva")
    st.dataframe(
        df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]].head(10),
        use_container_width=True
    )

    st.subheader("🚨 Países em Nível Crítico")
    df_critico = df_rank[df_rank["nivel_paz"] == "Crítico"]
    st.dataframe(
        df_critico[["country_name", "indicator_value"]],
        use_container_width=True
    )

    st.subheader("📊 Ranking Completo")
    st.dataframe(
        df_rank[["Posição", "country_name", "indicator_value", "nivel_paz"]],
        use_container_width=True
    )

    st.success("✅ Ranking carregado com sucesso.")

# ======================================
# PÁGINA: CONTADOR DE SÓIS
# ======================================
elif pagina == "Contador de Sóis":
    st.title("☀️ Contador Global de Sóis da Paz Viva")

    df = df_peacekeepers.copy()
    df_c = df_countries[["country_code", "country_name"]]

    total_suns = len(df)
    st.metric("☀️ Total Global de Sóis da Paz", total_suns)

    st.divider()

    df_country = df.groupby("country_code").size().reset_index(name="total")
    df_country = df_country.merge(df_c, on="country_code", how="left")
    df_country = df_country.sort_values(by="total", ascending=False)

    st.subheader("🌍 Sóis da Paz por País")
    st.dataframe(df_country[["country_name", "total"]], use_container_width=True)

    st.divider()

    df["ano_mes"] = df["created_at"].dt.to_period("M").astype(str)
    df_month = df.groupby("ano_mes").size().reset_index(name="total")

    st.subheader("📅 Evolução Mensal dos Sóis da Paz")
    st.dataframe(df_month, use_container_width=True)

    st.success("✅ Contador carregado com sucesso.")

# ======================================
# PÁGINA: EVOLUÇÃO GLOBAL DA PAZ
# ======================================
elif pagina == "Evolução Global da Paz":
    st.title("📈 Evolução Global da Paz Viva")

    df = df_index.copy()
    df["ano_mes"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    df_global = df.groupby("ano_mes")["indicator_value"].mean().reset_index()
    df_global.rename(columns={"indicator_value": "media_global"}, inplace=True)

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

    st.success("✅ Evolução global carregada com sucesso.")

# ======================================
# PÁGINA: RELATÓRIO MENSAL
# ======================================
elif pagina == "Relatório Mensal":
    st.title("📄 Relatório Mensal da Paz Viva")

    st.markdown("""
    Este relatório apresenta a **situação global da Paz Viva** para o período selecionado,
    com base no Índice Oficial da Paz Viva e nos Sóis do Movimento da Paz.
    """)

    st.sidebar.subheader("📅 Período do Relatório")

    anos = sorted(df_index["year"].unique())
    meses = sorted(df_index["month"].unique())

    ano_sel = st.sidebar.selectbox("Ano", anos, key="rel_ano")
    mes_sel = st.sidebar.selectbox("Mês", meses, key="rel_mes")

    df_mes = df_index[
        (df_index["year"] == ano_sel) &
        (df_index["month"] == mes_sel)
    ].copy()

    df_mes = df_mes.merge(df_countries[["country_code", "country_name"]], on="country_code", how="left")
    df_mes["nivel_paz"] = df_mes["indicator_value"].apply(classificar_paz)

    df_suns_copy = df_peacekeepers.copy()
    total_suns_global = len(df_suns_copy)
    df_suns_mes = df_suns_copy[
        (df_suns_copy["created_at"].dt.year == ano_sel) &
        (df_suns_copy["created_at"].dt.month == mes_sel)
    ]
    total_suns_mes = len(df_suns_mes)

    st.subheader("🌍 Visão Geral do Período")

    col1, col2, col3, col4 = st.columns(4)

    media_global = df_mes["indicator_value"].mean()
    num_paises = df_mes["country_code"].nunique()

    col1.metric("Índice Médio Global", f"{media_global:.1f}" if pd.notna(media_global) else "-")
    col2.metric("Países com dados no período", num_paises)
    col3.metric("Sóis da Paz neste mês", total_suns_mes)
    col4.metric("Sóis acumulados (global)", total_suns_global)

    st.markdown("---")

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
    3. Ajuste a orientação se desejar.  
    4. Clique em **Salvar**.
    """)

    st.success("✅ Relatório mensal pronto para impressão ou exportação em PDF.")
def mostrar_ranking():
    import streamlit as st
    import sqlite3
    import pandas as pd
    from pathlib import Path

    DB_PATH = Path("data/database/paz.db")

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
