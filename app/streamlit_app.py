import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import tempfile
from io import BytesIO

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
    Mapa vibracional global da consciência — a expansão da paz em ação
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
        color_continuous_scale=[
            (0.0, "#0f172a"),   # muito escuro (níveis mais baixos)
            (0.25, "#1e3a8a"),  # azul profundo
            (0.50, "#0284c7"),  # azul médio
            (0.70, "#7dd3fc"),  # azul bem claro
            (0.85, "#dcfce7"),  # verde muito claro (acima de ~80%)
            (1.0, "#ecfdf5"),   # verde quase branco (99–100%)
        ],
        range_color=(df["indicator_value"].min(), df["indicator_value"].max()),
        title="Distribuição Global do Índice de Paz",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para este período.")

# =========================
# MAPA HISTÓRICO DA PAZ — VERSÃO FINAL LIMPA E COMPATÍVEL
# =========================
import time

st.divider()
st.subheader("⏳ Mapa Histórico da Paz — Evolução da Consciência Global")

df_hist = df.copy()
df_hist["year"] = df_hist["year"].astype(int)
df_hist["month"] = df_hist["month"].astype(int)

df_hist["periodo"] = (
    df_hist["year"].astype(str)
    + "-"
    + df_hist["month"].astype(str).str.zfill(2)
)

df_hist = df_hist.sort_values(["year", "month"])
periodos = df_hist["periodo"].unique().tolist()

# =========================
# CASO 1 — NENHUM PERÍODO
# =========================
if len(periodos) == 0:
    st.warning("Ainda não há dados suficientes para gerar o mapa histórico.")

# =========================
# CASO 2 — APENAS 1 PERÍODO (SEM SLIDER, SEM PLAY)
# =========================
elif len(periodos) == 1:
    periodo_atual = periodos[0]

    st.info(f"Exibindo período único disponível: {periodo_atual}")

    dfp = df_hist[df_hist["periodo"] == periodo_atual]

    fig_hist = px.choropleth(
        dfp,
        locations="country_code",
        color="indicator_value",
        hover_name="country_code",
        color_continuous_scale=[
            (0.0, "#0f172a"),
            (0.25, "#1e3a8a"),
            (0.50, "#0284c7"),
            (0.70, "#7dd3fc"),
            (0.85, "#dcfce7"),
            (1.0, "#ecfdf5"),
        ],
        range_color=(
            df["indicator_value"].min(),
            df["indicator_value"].max()
        ),
        title=f"Mapa Histórico da Paz — {periodo_atual}"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.success("A animação será ativada automaticamente quando houver mais de um período histórico.")

# =========================
# CASO 3 — DOIS OU MAIS PERÍODOS (SLIDER + PLAY AUTOMÁTICO)
# =========================
else:
    if "slider_historico" not in st.session_state:
        st.session_state.slider_historico = 0

    st.markdown("### Seleção manual do período")

    periodo_idx = st.slider(
        "Selecione o período:",
        0,
        len(periodos) - 1,
        st.session_state.slider_historico
    )

    st.session_state.slider_historico = periodo_idx

    st.markdown("### Animação automática")
    col_play, col_vel, col_loop = st.columns([1, 1, 1])

    with col_play:
        iniciar_animacao = st.button("▶️ Play")

    with col_vel:
        velocidade = st.selectbox(
            "Velocidade",
            ["Lenta", "Normal", "Rápida"],
            index=1
        )

    with col_loop:
        loop = st.checkbox("Loop contínuo")

    if velocidade == "Lenta":
        delay = 1.2
    elif velocidade == "Rápida":
        delay = 0.3
    else:
        delay = 0.6

    mapa_container = st.empty()

    def desenhar_mapa(idx):
        periodo = periodos[idx]
        dfp = df_hist[df_hist["periodo"] == periodo]

        fig_hist = px.choropleth(
            dfp,
            locations="country_code",
            color="indicator_value",
            hover_name="country_code",
            color_continuous_scale=[
                (0.0, "#0f172a"),
                (0.25, "#1e3a8a"),
                (0.50, "#0284c7"),
                (0.70, "#7dd3fc"),
                (0.85, "#dcfce7"),
                (1.0, "#ecfdf5"),
            ],
            range_color=(
                df["indicator_value"].min(),
                df["indicator_value"].max()
            ),
            title=f"Mapa Histórico da Paz — {periodo}"
        )

        fig_hist.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        mapa_container.plotly_chart(fig_hist, use_container_width=True)

    # Desenho inicial
    desenhar_mapa(periodo_idx)

    # Execução da animação
    if iniciar_animacao:
        executando = True
        while executando:
            for i in range(0, len(periodos)):
                st.session_state.slider_historico = i
                desenhar_mapa(i)
                time.sleep(delay)

            if not loop:
                executando = False

        st.success("Animação concluída.")

# =========================
# CONTROLE UNIVERSAL (SEM ERRO)
# =========================

if len(periodos) == 0:
    st.warning("Ainda não há dados suficientes para gerar o mapa histórico.")

elif len(periodos) == 1:
    # Apenas um período → mostra direto, sem slider
    periodo_atual = periodos[0]
    st.info(f"Exibindo período único disponível: {periodo_atual}")

    df_periodo = df_hist[df_hist["periodo"] == periodo_atual]

    fig_hist = px.choropleth(
        df_periodo,
        locations="country_code",
        color="indicator_value",
        hover_name="country_code",
        color_continuous_scale=[
            (0.0, "#0f172a"),
            (0.25, "#1e3a8a"),
            (0.50, "#0284c7"),
            (0.70, "#7dd3fc"),
            (0.85, "#dcfce7"),
            (1.0, "#ecfdf5"),
        ],
        range_color=(
            df["indicator_value"].min(),
            df["indicator_value"].max()
        ),
        title=f"Mapa Histórico da Paz — {periodo_atual}"
    )

    fig_hist.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig_hist, use_container_width=True)

else:
    # Dois ou mais períodos → slider normal
    periodo_selecionado = st.slider(
        "Selecione o período:",
        0,
        len(periodos) - 1,
        len(periodos) - 1
    )

    df_periodo = df_hist[df_hist["periodo"] == periodos[periodo_selecionado]]

    fig_hist = px.choropleth(
        df_periodo,
        locations="country_code",
        color="indicator_value",
        hover_name="country_code",
        color_continuous_scale=[
            (0.0, "#0f172a"),
            (0.25, "#1e3a8a"),
            (0.50, "#0284c7"),
            (0.70, "#7dd3fc"),
            (0.85, "#dcfce7"),
            (1.0, "#ecfdf5"),
        ],
        range_color=(
            df["indicator_value"].min(),
            df["indicator_value"].max()
        ),
        title=f"Mapa Histórico da Paz — {periodos[periodo_selecionado]}"
    )

    fig_hist.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig_hist, use_container_width=True)

# =========================
# RELATÓRIOS COM GRÁFICOS (GLOBAL OU POR PAÍS)
# =========================
st.divider()
st.subheader("📊 Relatórios da Evolução da Paz")

st.markdown(
    "Geração de relatórios dinâmicos por **ano** ou por **meses dentro de um ano específico**, "
    "com opção de visualização **global** ou por **país individual**."
)

# =========================
# SELEÇÃO DE ESCOPO
# =========================
escopo = st.radio(
    "Selecione o escopo do relatório:",
    ["Global", "País específico"]
)

df_relatorio = df.copy()

if escopo == "País específico":
    paises = sorted(df["country_code"].unique())
    pais_escolhido = st.selectbox("Selecione o país:", paises)
    df_relatorio = df[df["country_code"] == pais_escolhido]

# =========================
# SELETOR DE MODO
# =========================
modo_relatorio = st.radio(
    "Selecione o tipo de relatório:",
    ["Relatório por Ano", "Relatório Mensal (Ano Específico)"]
)

# =========================
# RELATÓRIO POR ANO
# =========================
if modo_relatorio == "Relatório por Ano":
    if escopo == "Global":
        st.markdown("### 🌍 Evolução Anual da Paz Global")
    else:
        st.markdown(f"### 🏳️ Evolução Anual da Paz — {pais_escolhido}")

    df_anual = (
        df_relatorio.groupby("year", as_index=False)["indicator_value"]
        .mean()
        .sort_values("year")
    )

    st.write("Tabela Resumo Anual")
    st.dataframe(df_anual, use_container_width=True)

    fig_anual = px.line(
        df_anual,
        x="year",
        y="indicator_value",
        markers=True,
        title="Média do Índice de Paz por Ano"
    )

    fig_anual.update_layout(
        yaxis_title="Índice Médio de Paz",
        xaxis_title="Ano",
        margin=dict(l=0, r=0, t=60, b=0),
    )

    st.plotly_chart(fig_anual, use_container_width=True)

# =========================
# RELATÓRIO MENSAL POR ANO
# =========================
else:
    if escopo == "Global":
        st.markdown("### 🗓️ Evolução Mensal da Paz Global — Ano Selecionado")
    else:
        st.markdown(f"### 🏳️ Evolução Mensal da Paz — {pais_escolhido}")

    anos_disponiveis = sorted(df_relatorio["year"].unique())
    ano_escolhido = st.selectbox("Selecione o ano:", anos_disponiveis)

    df_mensal = (
        df_relatorio[df_relatorio["year"] == ano_escolhido]
        .groupby("month", as_index=False)["indicator_value"]
        .mean()
        .sort_values("month")
    )

    st.write(f"Tabela Mensal — Ano {ano_escolhido}")
    st.dataframe(df_mensal, use_container_width=True)

    fig_mensal = px.line(
        df_mensal,
        x="month",
        y="indicator_value",
        markers=True,
        title=f"Evolução Mensal do Índice de Paz — {ano_escolhido}"
    )

    fig_mensal.update_layout(
        yaxis_title="Índice Médio de Paz",
        xaxis_title="Mês",
        margin=dict(l=0, r=0, t=60, b=0),
    )

    st.plotly_chart(fig_mensal, use_container_width=True)

# ======================================
# EXPORTAÇÃO EM PDF DOS RELATÓRIOS
# ======================================
from io import BytesIO
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import tempfile

st.divider()
st.subheader("📄 Exportar Relatório em PDF")

st.markdown(
    "Gere um relatório em PDF com o conteúdo exibido acima, incluindo gráficos, "
    "tabelas e informações do período selecionado."
)

# HTML base do PDF
def gerar_html_do_relatorio(escopo, modo_relatorio, pais=None, ano=None, tabela=None, grafico_html=None):
    titulo = "Relatório do Índice Global de Paz"
    if escopo == "País específico":
        titulo += f" — {pais}"

    subtitulo = modo_relatorio
    if ano:
        subtitulo += f" — {ano}"

    tabela_html = tabela.to_html(index=False)

    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 30px;
                }}
                h1 {{
                    color: #1a365d;
                }}
                h2 {{
                    color: #2d3748;
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 12px;
                    text-align: center;
                    color: #555;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                table, th, td {{
                    border: 1px solid #aaa;
                    padding: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <h2>{subtitulo}</h2>

            <h3>Tabela</h3>
            {tabela_html}

            <h3>Gráfico</h3>
            {grafico_html}

            <div class="footer">
                Movimento da Paz Global — Relatório Gerado Automaticamente
            </div>
        </body>
    </html>
    """
    return html

# Capturar escopo e dados do relatório já renderizados acima
if escopo == "Global":
    pais_for_pdf = None
else:
    pais_for_pdf = pais_escolhido

if modo_relatorio == "Relatório por Ano":
    tabela_for_pdf = df_anual
    grafico_html = fig_anual.to_html(full_html=False)
    ano_for_pdf = None
else:
    tabela_for_pdf = df_mensal
    grafico_html = fig_mensal.to_html(full_html=False)
    ano_for_pdf = ano_escolhido

# Botão PDF
if st.button("📄 Baixar PDF"):
    with st.spinner("Gerando PDF..."):
        html = gerar_html_do_relatorio(
            escopo,
            modo_relatorio,
            pais=pais_for_pdf,
            ano=ano_for_pdf,
            tabela=tabela_for_pdf,
            grafico_html=grafico_html
        )
