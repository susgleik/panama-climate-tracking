import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, get_stations, MONTH_NAMES_ES

st.set_page_config(page_title="Por Estación", layout="wide", page_icon="📍")

df = load_data()

st.title("📍 Análisis por Estación")

station = st.selectbox("Seleccionar estación", get_stations(df))
sdf = df[df["Estacion"] == station].copy()

# --- Métricas ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Temp. Máx. Registrada", f"{sdf['Tmax'].max():.1f} °C")
col2.metric("Temp. Mín. Registrada", f"{sdf['Tmin'].min():.1f} °C")
col3.metric("Precip. Total Anual", f"{sdf['Prcp'].sum():,.1f} mm")
col4.metric("Vel. Viento Promedio", f"{sdf['Wspd'].mean():.1f} km/h")

st.divider()

# --- Gráfico: Temperaturas (máx, mín, promedio) ---
st.subheader("Temperaturas Diarias")

fig = go.Figure()
fig.add_trace(go.Scatter(x=sdf["Date"], y=sdf["Tmax"], name="Máxima", line=dict(color="#ef4444")))
fig.add_trace(go.Scatter(x=sdf["Date"], y=sdf["Tavg"], name="Promedio", line=dict(color="#f59e0b")))
fig.add_trace(go.Scatter(x=sdf["Date"], y=sdf["Tmin"], name="Mínima", line=dict(color="#3b82f6")))
fig.update_layout(
    yaxis_title="Temperatura (°C)",
    xaxis_title="Fecha",
    height=420,
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig, use_container_width=True)

# --- Gráfico: Precipitación mensual ---
st.subheader("Precipitación Mensual")

sdf["month_num"] = sdf["Date"].dt.month
monthly = sdf.groupby("month_num").agg({"Prcp": "sum"}).reset_index()
monthly["Mes"] = monthly["month_num"].map(MONTH_NAMES_ES)

fig2 = px.bar(
    monthly,
    x="Mes",
    y="Prcp",
    labels={"Prcp": "Precipitación (mm)", "Mes": ""},
    color="Prcp",
    color_continuous_scale="Blues",
)
fig2.update_layout(height=380, showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico: Distribución dirección del viento ---
st.subheader("Distribución de Dirección del Viento")

wdir_counts = sdf["Wdir"].value_counts().reset_index()
wdir_counts.columns = ["Dirección", "Días"]

fig3 = px.bar(
    wdir_counts,
    x="Dirección",
    y="Días",
    color="Días",
    color_continuous_scale="Viridis",
)
fig3.update_layout(height=350)
st.plotly_chart(fig3, use_container_width=True)
