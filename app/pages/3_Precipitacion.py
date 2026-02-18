import streamlit as st
import plotly.express as px
from utils import load_data, MONTH_NAMES_ES

st.set_page_config(page_title="Precipitación", layout="wide", page_icon="🌧️")

df = load_data()

st.title("🌧️ Análisis de Precipitación")

# --- Precipitación total anual por estación ---
st.subheader("Precipitación Total Anual por Estación")

annual = df.groupby(["Provincia", "Estacion"]).agg({"Prcp": "sum"}).reset_index()
annual = annual.sort_values("Prcp", ascending=True)

fig = px.bar(
    annual,
    x="Prcp",
    y="Estacion",
    color="Provincia",
    orientation="h",
    labels={"Prcp": "Precipitación Total (mm)", "Estacion": ""},
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Mapa de calor: precipitación mensual por estación ---
st.subheader("Precipitación Mensual por Estación")

df_copy = df.copy()
df_copy["month_num"] = df_copy["Date"].dt.month
heatmap_data = df_copy.groupby(["Estacion", "month_num"]).agg({"Prcp": "sum"}).reset_index()
heatmap_pivot = heatmap_data.pivot(index="Estacion", columns="month_num", values="Prcp")
heatmap_pivot = heatmap_pivot.rename(columns=MONTH_NAMES_ES)

fig2 = px.imshow(
    heatmap_pivot,
    labels=dict(x="Mes", y="Estación", color="Precip. (mm)"),
    color_continuous_scale="Blues",
    aspect="auto",
)
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Días con lluvia vs sin lluvia ---
st.subheader("Días con Lluvia vs Sin Lluvia")

df_copy["Llovió"] = df_copy["Prcp"].apply(lambda x: "Con lluvia" if x > 0 else "Sin lluvia")
rain_counts = df_copy.groupby(["Estacion", "Llovió"]).size().reset_index(name="Días")

fig3 = px.bar(
    rain_counts,
    x="Estacion",
    y="Días",
    color="Llovió",
    barmode="stack",
    labels={"Estacion": "Estación"},
    color_discrete_map={"Con lluvia": "#3b82f6", "Sin lluvia": "#f59e0b"},
)
fig3.update_layout(height=400, legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig3, use_container_width=True)
