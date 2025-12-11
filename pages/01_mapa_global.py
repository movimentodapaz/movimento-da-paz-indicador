# 01_mapa_global.py
# Página Streamlit: Mapa Global Interativo - Portal da Paz Viva
# Requisitos: streamlit, folium, streamlit-folium, pandas, branca

import sqlite3
from typing import Optional

import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import branca.colormap as cm

st.set_page_config(page_title="Mapa Global - Portal da Paz Viva", layout="wide")

DB_PATH = "app/data/database/paz.db"

# ---------- Utilitários ----------
@st.cache_data(ttl=600)
def load_tables(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        country_meta = pd.read_sql_query("SELECT * FROM country_metadata", conn)
    except Exception:
        country_meta = pd.DataFrame()

    try:
        country_metrics = pd.read_sql_query("SELECT * FROM country_metrics", conn)
    except Exception:
        country_metrics = pd.DataFrame()

    conn.close()
    return country_meta, country_metrics


@st.cache_data(ttl=600)
def prepare_aggregated(df_meta: pd.DataFrame, df_metrics: pd.DataFrame, year: Optional[int], month: Optional[int], aggregation: str):
    """Join metadata and metrics and aggregate per country according to selection.
    aggregation: 'latest' | 'mean' | 'median' | 'sum'
    If year/month are None, uses latest available in the metrics table.
    """
    if df_metrics.empty:
        return pd.DataFrame()

    metrics = df_metrics.copy()

    # If year/month not provided, pick latest period
    if year is None:
        year = int(metrics['year'].max())
    if month is None:
        # pick latest month for that year
        sub = metrics[metrics['year'] == year]
        if not sub.empty:
            month = int(sub['month'].max())
        else:
            month = int(metrics['month'].max())

    # Filter to selected year/month for 'latest' view; for 'mean' or others consider year range
    if aggregation == 'latest':
        sel = metrics[(metrics['year'] == year) & (metrics['month'] == month)]
        agg = sel.groupby('country_code', as_index=False)['indicator_value'].mean()
    else:
        # aggregate across selected year (if provided) otherwise all time
        if year is not None:
            sel = metrics[metrics['year'] == year]
        else:
            sel = metrics
        if sel.empty:
            agg = pd.DataFrame(columns=['country_code', 'indicator_value'])
        else:
            if aggregation == 'mean':
                agg = sel.groupby('country_code', as_index=False)['indicator_value'].mean()
            elif aggregation == 'median':
                agg = sel.groupby('country_code', as_index=False)['indicator_value'].median()
            elif aggregation == 'sum':
                agg = sel.groupby('country_code', as_index=False)['indicator_value'].sum()
            else:
                agg = sel.groupby('country_code', as_index=False)['indicator_value'].mean()

    # Join with metadata
    if df_meta.empty:
        merged = agg
    else:
        merged = agg.merge(df_meta, on='country_code', how='left')

    # Clean and rename
    merged = merged.rename(columns={'indicator_value': 'paz_value'})
    # drop rows without coordinates
    merged = merged.dropna(subset=['latitude', 'longitude'])

    return merged


# ---------- UI ----------
st.title("Mapa Global — Portal da Paz Viva")
st.markdown(
    "Este mapa mostra o Indicador de Paz Viva por país. Use os controles à esquerda para filtrar o período e o tipo de agregação."
)

# Load data
country_meta, country_metrics = load_tables()

if country_metrics.empty or country_meta.empty:
    st.warning("Os dados não foram encontrados ou estão incompletos. Verifique `app/data/database/paz.db` e as tabelas 'country_metadata' e 'country_metrics'.")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.header("Filtros")

    years = sorted(country_metrics['year'].dropna().unique().astype(int).tolist())
    months = sorted(country_metrics['month'].dropna().unique().astype(int).tolist())

    default_year = years[-1] if years else None
    default_month = months[-1] if months else None

    year = st.selectbox("Ano", options=[None] + years, index=(len(years) if default_year is None else years.index(default_year) + 1))
    month = st.selectbox("Mês", options=[None] + months, index=(len(months) if default_month is None else months.index(default_month) + 1))

    aggregation = st.selectbox("Agregação", options=['latest', 'mean', 'median', 'sum'], index=0, help='latest = valor do ano/mês selecionado; mean/median/sum = agregação por país no ano selecionado')

    show_heatmap = st.checkbox("Exibir Heatmap", value=True)
    show_clusters = st.checkbox("Agrupar marcadores (MarkerCluster)", value=True)
    min_radius = st.slider("Raio mínimo dos círculos", 2, 20, 6)

    st.markdown("---")
    st.markdown("**Exportar dados**")

# ---------- Prepare data for map ----------
agg_df = prepare_aggregated(country_meta, country_metrics, year, month, aggregation)
if agg_df.empty:
    st.info("Nenhum dado disponível para a seleção. Tente outro ano/mês.")
    st.stop()

# Normalize paz_value for circle size and colormap
vmin = float(agg_df['paz_value'].min())
vmax = float(agg_df['paz_value'].max())

# Create a color map (higher paz_value -> greener)
colormap = cm.LinearColormap(['red', 'orange', 'yellow', 'lightgreen', 'green'], vmin=vmin, vmax=vmax)
colormap = colormap.to_step(index=[vmin, vmin + (vmax - vmin) * 0.25, vmin + (vmax - vmin) * 0.5, vmin + (vmax - vmin) * 0.75, vmax])

# center map on mean coords
center_lat = agg_df['latitude'].mean()
center_lon = agg_df['longitude'].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=2, tiles='CartoDB positron')

# Heatmap layer
if show_heatmap:
    heat_data = agg_df[['latitude', 'longitude', 'paz_value']].values.tolist()
    HeatMap(heat_data, radius=25, blur=15, max_zoom=6).add_to(m)

# Marker cluster
if show_clusters:
    cluster = MarkerCluster(name='Países', control=False).add_to(m)

# Add circle markers
for _, row in agg_df.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    country = row.get('country_name') or row.get('country_code')
    value = row['paz_value']

    color = colormap(value)
    # size scaled between min_radius and min_radius*4
    normalized = 0 if vmax == vmin else (value - vmin) / (vmax - vmin)
    radius = min_radius + int(normalized * min_radius * 3)

    tooltip_html = f"<b>{country}</b><br/>Valor: {value:.3f}<br/>Código: {row.get('country_code', '')}"

    circle = folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(tooltip_html, max_width=350)
    )

    if show_clusters:
        circle.add_to(cluster)
    else:
        circle.add_to(m)

# Add colormap as legend
colormap.caption = 'Indicador de Paz Viva'
colormap.add_to(m)

# Layer control
folium.LayerControl().add_to(m)

# ---------- Streamlit layout ----------
left_col, right_col = st.columns((2, 1))

with left_col:
    st.subheader('Mapa interativo')
    st_data = st_folium(m, width="100%", height=700)

with right_col:
    st.subheader('Resumo')
    st.write(f"Países exibidos: {len(agg_df)}")
    st.write("Período selecionado.")

    st.markdown('---')
    st.write('Valores (estatísticas)')
    st.write(agg_df['paz_value'].describe())

    # Top / Bottom lists
    top10 = agg_df.sort_values('paz_value', ascending=False).head(10)
    bottom10 = agg_df.sort_values('paz_value', ascending=True).head(10)

    st.markdown('**Top 10 (maior paz)**')
    st.table(top10[['country_name', 'country_code', 'paz_value']].set_index('country_name'))

    st.markdown('**Bottom 10 (menor paz)**')
    st.table(bottom10[['country_name', 'country_code', 'paz_value']].set_index('country_name'))

    # Download CSV
    csv = agg_df.to_csv(index=False)
    st.download_button('Download CSV (dados do mapa)', data=csv, file_name='mapa_paz_viva.csv', mime='text/csv')

st.markdown('\n---\n')
st.caption('Mapa gerado a partir das tabelas `country_metadata` e `country_metrics` da base paz.db')
