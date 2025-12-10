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
body { background-color: #f7fbff; }
.main-title {
    font-size: 42px; font-weight: 700; color: #d4af37;
    text-align: center; margin-bottom: 0;
}
.sub-title {
    font-size: 18px; color: #3b82f6;
    text-align: center; margin-top: 0; margin-bottom: 30px;
}
.kpi-card {
    background: white; padding: 20px; border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    text-align: center;
}
.kpi-title { font-size: 14px; color: #3b82f6; }
.kpi-value { font-size: 32px; font-weight: 700; color: #d4af37; }
.sidebar-title {
    font-size: 22px; font-weight: 700; color: #d4af37;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO PRINCIPAL
# =========================
st.markdown("<div class='main-title'>Indicador de Paz — Movimento da Paz</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Mapa Vibracional Global da Consciência</div>", unsafe_allow_html=True)

# =========================
# CAMINHO DO BANCO
# =========================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database" / "paz.db"

st.sidebar.markdown("<div class='sidebar-title'>Filtros</div>", unsafe_allow_html=True)
st.sidebar.write(f"🗄️ Banco: `{DB_PATH}`")

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
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Nível Médio de Paz</div>
        <div class='kpi-value'>{media_paz}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>País em Destaque</div>
        <div class='kpi-value'>{pais_lider}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Total de Registros</div>
        <div class='kpi-value'>{total_registros}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Tendência</div>
        <div class='kpi-value'>{tendencia}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# MAPA PRINCIPAL
# =========================
st.subheader(f"🌍 Mapa Global da Paz — {ano}/{mes}")

if len(df_filtrado) > 0:
    fig = px.choropleth(
        df_filtrado,
        locations="country_code",
        color="indicator_value",
        hover_name="country_code",
        color_continuous_scale="sunset",
        range_color=(df["indicator_value"].min(), df["indicator_value"].max()),
        title="Distribuição Global do Índice de Paz"
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
st.info("Esta seção permitirá visualizar a evolução vibracional da paz ao longo do tempo.")
