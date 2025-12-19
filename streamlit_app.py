import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA (SEO)
# =========================

st.set_page_config(
    page_title="Movimento da Paz Viva | Mapa Global dos Pacificadores",
    layout="wide"
)

# =========================
# META DESCRIPTION (SEO)
# =========================

st.markdown(
    """
    <meta name="description" content="
    Movimento da Paz Viva — Mapa global dos Pacificadores.
    Visualização interativa da expansão da paz no planeta,
    com dados reais, metodologia ética e distribuição geográfica
    por cidade e país.
    ">
    """,
    unsafe_allow_html=True
)

# =========================
# TEXTO INDEXÁVEL (PARA BUSCADORES)
# =========================

st.markdown("""
# 🌍 Movimento da Paz Viva

O **Movimento da Paz Viva** é uma iniciativa consciente que demonstra,
de forma ética e verificável, como a **paz interior sustentada por indivíduos**
gera impacto coletivo mensurável no mundo.

Por meio de um **mapa global interativo**, o projeto apresenta a
**distribuição geográfica dos Pacificadores** — pessoas que escolheram
viver e irradiar a paz como prática diária.

Os dados apresentados são públicos, agregados e auditáveis,
respeitando integralmente a privacidade individual.
""")

# =========================
# REDIRECIONAMENTO PARA O MAPA
# =========================

st.switch_page("pages/04_mapa_pacificadores.py")
