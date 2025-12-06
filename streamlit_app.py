# app/streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import pycountry
import plotly.express as px
import os

st.set_page_config(page_title="Indicador de Paz — Movimento da Paz", layout="wide")
st.title("Indicador de Paz — Movimento da Paz")

def iso3_from_country(name: str):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except Exception:
        return None

def sample_data():
    data = {
        "country": ["Norway","Sweden","Brazil","South Africa","Ukraine","Afghanistan","USA","India","Mexico","Syria"],
        "homicide_per_100k":[0.5,1.0,27.0,35.9,6.5,5.2,5.0,3.2,29.0,12.0],
        "battle_deaths_per_100k":[0.0,0.0,0.1,0.2,45.0,120.0,0.5,0.1,0.2,300.0],
        "conflict_event_rate":[0.1,0.2,3.0,5.5,80.0,200.0,2.0,1.5,4.0,400.0],
        "va_women_per_100k":[2.0,3.0,60.0,120.0,25.0,40.0,30.0,20.0,70.0,80.0],
        "military_spend_per_capita":[600,500,200,250,300,150,700,50,100,20],
        "displaced_per_100k":[0.0,0.0,50.0,300.0,20000.0,40000.0,50.0,10.0,500.0,50000.0],
    }
    df = pd.DataFrame(data)
    df["iso3"] = df["country"].apply(iso3_from_country)
    return df

def minmax_worse_is_high(series: pd.Series):
    if series.max() == series.min():
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def harmonize_and_compute_ip(df: pd.DataFrame, weights: dict):
    required = ["country","homicide_per_100k","battle_deaths_per_100k","conflict_event_rate",
                "va_women_per_100k","military_spend_per_capita","displaced_per_100k"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {c}")

    norm = pd.DataFrame(index=df.index)
    for col in weights.keys():
        norm[col + "_norm"] = minmax_worse_is_high(df[col].astype(float))

    V = np.zeros(len(df))
    for col, w in weights.items():
        V = V + norm[col + "_norm"].values * w

    df = pd.concat([df, norm], axis=1)
    df["V_score"] = V
    df["IP_0_100"] = 100 * (1 - df["V_score"])

    # Índice Vibracional de Paz (VibIndex) — exemplo: combina IP técnico com fatores positivos
    # Fórmula simplificada: VibIndex = (IP_0_100 * 8) + (fator_bemestar)
    # fator_bemestar: placeholder — aumente quando tiver Gallup / HDI / Percepção de segurança
    df["fator_bemestar"] = 50  # placeholder fixo (ajustar com dados reais)
    df["VibIndex_0_1000"] = (df["IP_0_100"] * 8) + df["fator_bemestar"]
    df["VibIndex_0_1000"] = df["VibIndex_0_1000"].clip(0, 1000)

    return df

# Sidebar: pesos
st.sidebar.header("Configuração de pesos (soma será normalizada)")
w_homicide = st.sidebar.slider("Homicídios", 0.0, 1.0, 0.25, 0.01)
w_battle = st.sidebar.slider("Mortes por conflito", 0.0, 1.0, 0.25, 0.01)
w_events = st.sidebar.slider("Eventos (ACLED)", 0.0, 1.0, 0.20, 0.01)
w_va = st.sidebar.slider("Violência contra mulheres", 0.0, 1.0, 0.15, 0.01)
w_mil = st.sidebar.slider("Gasto militar", 0.0, 1.0, 0.10, 0.01)
w_disp = st.sidebar.slider("Deslocados", 0.0, 1.0, 0.05, 0.01)

weights_raw = {
    "homicide_per_100k": w_homicide,
    "battle_deaths_per_100k": w_battle,
    "conflict_event_rate": w_events,
    "va_women_per_100k": w_va,
    "military_spend_per_capita": w_mil,
    "displaced_per_100k": w_disp,
}
total = sum(weights_raw.values())
if total == 0:
    st.sidebar.warning("Todos os pesos são zero — usando padrão.")
    weights = {"homicide_per_100k":0.25,"battle_deaths_per_100k":0.25,"conflict_event_rate":0.20,"va_women_per_100k":0.15,"military_spend_per_capita":0.10,"displaced_per_100k":0.05}
else:
    weights = {k: v/total for k,v in weights_raw.items()}

mode = st.sidebar.selectbox("Modo", ["DEMO — dados sintéticos", "REAL — usar APIs"])
run = st.sidebar.button("Executar pipeline")

if run:
    if mode.startswith("DEMO"):
        df = sample_data()
    else:
        st.warning("Modo REAL selecionado. Implemente hooks para baixar e harmonizar as fontes nas funções apropriadas.")
        df = sample_data()

    result = harmonize_and_compute_ip(df.copy(), weights)

    st.subheader("Ranking — Indicador de Paz (IP)")
    st.dataframe(result[["country","iso3","IP_0_100","V_score","VibIndex_0_1000"]].sort_values("IP_0_100", ascending=False))

    fig = px.bar(result.sort_values("IP_0_100", ascending=False), x="country", y="IP_0_100", labels={"IP_0_100":"Indicador de Paz (0-100)"})
    st.plotly_chart(fig, use_container_width=True)

    if result["iso3"].notnull().sum() > 0:
        map_df = result.dropna(subset=["iso3"]).copy()
        choropleth = px.choropleth(map_df, locations="iso3", color="IP_0_100", color_continuous_scale=px.colors.sequential.Plasma)
        st.plotly_chart(choropleth, use_container_width=True)
    else:
        st.info("Códigos ISO3 ausentes — não foi possível desenhar o mapa.")
        