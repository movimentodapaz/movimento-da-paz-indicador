import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database" / "paz.db"


# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(page_title="Indicador de Paz — Movimento da Paz", layout="wide")
st.title("Indicador de Paz — Movimento da Paz")

# ============================================
# LOCALIZAÇÃO ROBUSTA DO BANCO SQLITE
# ============================================
BASE_DIR = Path(__file__).resolve().parent

candidatos = [
    BASE_DIR / "data" / "database" / "paz.db",
    BASE_DIR.parent / "data" / "database" / "paz.db",
]

DB_PATH = None
for caminho in candidatos:
    if caminho.exists():
        DB_PATH = caminho
        break

if DB_PATH is None:
    st.error(
        "❌ Banco de dados `paz.db` não foi encontrado.\n\n"
        "Caminhos verificados:\n"
        + "\n".join(f"- {c}" for c in candidatos)
    )
    st.stop()

# Opcional: exibir caminho do banco para depuração
st.caption(f"🗄️ Usando banco de dados em: `{DB_PATH}`")

# ============================================
# FUNÇÃO PARA CARREGAR DADOS AGREGADOS
# ============================================
def load_aggregated(year: int, month: int) -> pd.DataFrame:
    """Carrega o índice de paz por país a partir do SQLite.

    Se houver erro de SQLite, exibe a causa na tela e retorna DataFrame vazio.
    """
    try:
        conn = sqlite3.connect(DB_PATH)

        query = """
            SELECT 
                c.country_code AS country_iso3,
                c.country_name,
                m.indicator_value AS peace_score_0_100
            FROM country_metrics m
            JOIN country_metadata c
              ON m.country_code = c.country_code
            WHERE m.year = ? AND m.month = ?
        """

        df = pd.read_sql_query(query, conn, params=(year, month))
        conn.close()
        return df

    except sqlite3.OperationalError as e:
        st.error(
            "⚠️ Erro ao acessar o banco SQLite (OperationalError):\n\n"
            f"`{e}`\n\n"
            "Verifique se as tabelas `country_metrics` e `country_metadata` "
            "existem e se foram criadas corretamente."
        )
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Erro inesperado ao carregar dados: `{e}`")
        return pd.DataFrame()

# ============================================
# FILTROS (ANO / MÊS)
# ============================================
col1, col2 = st.columns([3, 1])
with col2:
    st.header("Filtro")
    year = st.selectbox("Ano", options=list(range(2025, 2031)), index=0)
    month = st.selectbox("Mês", options=list(range(1, 13)), index=0)

# ============================================
# MAPA GLOBAL DA PAZ
# ============================================
st.subheader(f"Mapa Global — Paz ({year}-{month:02d})")

agg = load_aggregated(year, month)

if agg.empty:
    st.warning(
        "Nenhum dado encontrado para este período.\n\n"
        "Se você acabou de criar o banco, verifique se há registros em "
        "`country_metrics` para o ano/mês selecionado."
    )
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
