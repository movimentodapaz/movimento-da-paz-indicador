import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px

# =========================
# CONFIG GERAL DA PÁGINA
# =========================
st.set_page_config(
    page_title="Indicador de Paz — Movimento da Paz",
    page_icon="🌍",
    layout="wide"
)

# =========================
# ESTILO VISUAL (CSS)
# =========================
st.markdown("""
<style>
/* Fundo geral do app */
.stApp {
    background-color: #f3f7ff;
}

/* Cabeçalho com faixa dourado + azul */
.header-container {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8);
    border-radius: 0 0 28px 28px;
    padding: 24px 16px 32px 16px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
}
.header-title {
    font-size: 40px;
    font-weight: 800;
    text-align: center;
    color: #facc15;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.header-subtitle {
    font-size: 18px;
    text-align: center;
    color: #e0f2fe;
    font-weight: 500;
}

/* Cards de KPI */
.kpi-card {
    background: #ffffff;
    padding: 18px 14px;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.10);
    text-align: center;
    border: 1px solid rgba(148, 163, 184, 0.35);
}
.kpi-title {
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #d4af37;
}

/* Sidebar */
.sidebar-title {
    font-size: 20px;
    font-weight: 700;
    color: #d4af37;
    margin-bottom: 8px;
}
.sidebar-caption {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CABEÇALHO
# =========================
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">INDICADOR DE PAZ — MOVIMENTO DA PAZ</div>
        <div class="header-subtitle">
            Mapa vibracional global da consciência — da guerra ao Amor em ação
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# CAMINHO DO BANCO
# =========================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database" / "paz.db"

# =========================
# SIDEBAR (Filtros)
# =========================
st.sidebar.markdown("<div class='sidebar-title'>Filtros</div>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div class='sidebar-caption'>Selecione o período que deseja visualizar no mapa global.</div>",
    unsafe_allow_html=True,
)

# =========================
# CONEXÃO COM BANCO
# =========================
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM country_metrics", conn)
    conn.close()
    return df

df = carregar_dados()

# =========================
# FILTROS
# =========================
anos = sorted(df["year"].unique())
meses = sorted(df["month"].unique())

ano = st.sidebar.selectbox("Ano", anos[::-1])
mes = st.sidebar.selectbox("Mês", meses)

df_filtrado = df[(df["year"] == ano) & (df["month"] == mes)]

# =========================
# KPI / INDICADORES
# =========================
col1, col2, col3, col4 = st.columns(4)

if len(df_filtrado) > 0:
    media_paz = round(df_filtrado["indicator_value"].mean(), 2)
    pais_lider = df_filtrado.sort_values("indicator_value", ascending=False).iloc[0]["country_code"]
    total_registros = len(df_filtrado)
    tendencia = "Estável"
else:
    media_paz = 0
    pais_lider = "-"
    total_registros = 0
    tendencia = "-"

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Nível médio de paz</div>
            <div class="kpi-value">{media_paz}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Código em maior paz</div>
            <div class="kpi-value">{pais_lider}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total de registros</div>
            <div class="kpi-value">{total_registros}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Tendência</div>
            <div class="kpi-value">{tendencia}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# =========================
# MAPA PRINCIPAL
# =========================
st.subheader(f"🌍 Mapa Global da Paz — {ano}/{mes:02d}")

if len(df_filtrado) > 0:
    fig = px.choropleth(
        df_filtrado,
        locations="country_code",
        color="indicator_value",
        hover_name="country_code",
        color_continuous_scale="sunset",
        range_color=(df["indicator_value"].min(), df["indicator_value"].max()),
        title="Distribuição Global do Índice de Paz",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para este período.")

# =========================
# BASE PARA MAPA HISTÓRICO
# =========================
st.divider()
st.subheader("⏳ Mapa Histórico da Paz (Em Construção)")
st.info(
    "Esta seção permitirá visualizar a evolução vibracional da paz ao longo do tempo, "
    "com animação mês a mês e narrativa histórica dos saltos de consciência."
)
