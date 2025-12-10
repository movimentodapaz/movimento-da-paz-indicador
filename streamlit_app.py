# app/streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from db.models import engine
import sqlalchemy as sa

st.set_page_config(page_title="Indicador de Paz — Movimento da Paz", layout="wide")
st.title("Indicador de Paz — Movimento da Paz")

def load_aggregated(year, month):
    q = f"""
    SELECT * FROM aggregated_monthly WHERE year = {year} AND month = {month}
    """
    with engine.connect() as conn:
        df = pd.read_sql(q, conn)
    return df

def load_instagram(year, month):
    q = f"""
    SELECT country_iso3, followers_count FROM instagram_followers WHERE year = {year} AND month = {month}
    """
    with engine.connect() as conn:
        df = pd.read_sql(q, conn)
    return df

col1, col2 = st.columns([3,1])
with col2:
    st.header("Filtro")
    year = st.selectbox("Ano", options=list(range(2025, 2031)), index=0)
    month = st.selectbox("Mês", options=list(range(1,13)), index=0)

st.subheader(f"Mapa Global — Paz ({year}-{month:02d})")
agg = load_aggregated(year, month)
if agg.empty:
    st.warning("Nenhum dado agregado encontrado para este período. Execute o pipeline.")
else:
    # choropleth by peace_score
    fig = px.choropleth(agg, locations="country_iso3", color="peace_score_0_100",
                        color_continuous_scale="Blues", range_color=(0,100),
                        title="Peace Score (0-100)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Mapa de Pacificadores do Movimento da Paz")
ins_df = load_instagram(year, month)
if ins_df.empty:
    st.info("Nenhum dado de Instagram encontrado. Faça upload via scripts/collect_instagram.py")
else:
    # need lat/lon for iso3 -> use simple lookup via pycountry + fallback CSV
    import pycountry
    def iso3_to_centroid(iso3):
        # simple world centroids file could be added; try geopy? For now, use worldcountries CSV if exists
        return None
    # For simplicity we'll use a built-in mapping file if present
    centroids_path = os.path.join(os.path.dirname(__file__), "..", "data", "external", "country_centroids.csv")
    if os.path.exists(centroids_path):
        cdf = pd.read_csv(centroids_path)
        ins = ins_df.merge(cdf, left_on="country_iso3", right_on="iso3", how="left")
        ins = ins[ins["latitude"].notnull()]
        # marker size by followers_count
        ins["size"] = (ins["followers_count"] / ins["followers_count"].max()) * 30 + 5
        fig2 = px.scatter_geo(ins, lat="latitude", lon="longitude",
                              size="size", hover_name="country_iso3",
                              projection="natural earth",
                              title="Pacificadores (seguidores) — cada ponto = seguidor proporcional")
        fig2.update_traces(marker=dict(color="goldenrod", opacity=0.9, line=dict(width=0)))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Adicione file data/external/country_centroids.csv com columns: iso3,latitude,longitude")
