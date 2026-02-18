import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, get_stations, LABELS

st.set_page_config(
    page_title="Climate Tracking Panamá 2024",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_data()

# --- Encabezado ---
st.title("⛅ Climate Tracking Panamá 2024")
st.markdown("Datos climáticos diarios de **4 estaciones meteorológicas** en Panamá")

# --- Métricas generales ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Estaciones", df["Estacion"].nunique())
col2.metric("Provincias", df["Provincia"].nunique())
col3.metric("Registros", f"{len(df):,}")
col4.metric("Temp. Promedio", f"{df['Tavg'].mean():.1f} °C")

st.divider()

# --- Filtros en sidebar ---
st.sidebar.header("Filtros")

stations = st.sidebar.multiselect(
    "Estación",
    options=get_stations(df),
    default=get_stations(df),
)
filtered = df[df["Estacion"].isin(stations)]

date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(df["Date"].min(), df["Date"].max()),
    min_value=df["Date"].min(),
    max_value=df["Date"].max(),
)

if len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"] >= pd.to_datetime(date_range[0]))
        & (filtered["Date"] <= pd.to_datetime(date_range[1]))
    ]

# --- Gráfico: Temperatura promedio ---
st.subheader("Temperatura Promedio Diaria")

fig_temp = px.line(
    filtered,
    x="Date",
    y="Tavg",
    color="Estacion",
    labels={"Tavg": "Temperatura (°C)", "Date": "Fecha", "Estacion": "Estación"},
)
fig_temp.update_layout(height=420, legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig_temp, use_container_width=True)

# --- Gráfico: Precipitación ---
st.subheader("Precipitación Diaria")

fig_prcp = px.area(
    filtered,
    x="Date",
    y="Prcp",
    color="Estacion",
    labels={"Prcp": "Precipitación (mm)", "Date": "Fecha", "Estacion": "Estación"},
)
fig_prcp.update_layout(height=380, legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig_prcp, use_container_width=True)

# --- Tabla de datos ---
with st.expander("Ver datos en tabla"):
    st.dataframe(
        filtered.sort_values(["Estacion", "Date"]),
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV filtrado", csv, "climate_data_filtered.csv", "text/csv")
