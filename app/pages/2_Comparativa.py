import streamlit as st
import plotly.express as px
from utils import load_data, LABELS

st.set_page_config(page_title="Comparativa", layout="wide", page_icon="📊")

df = load_data()

st.title("📊 Comparativa entre Estaciones")

variable = st.selectbox("Variable a comparar", list(LABELS.keys()), format_func=lambda x: LABELS[x])

# --- Boxplot comparativo ---
st.subheader(f"Distribución de {LABELS[variable]}")

fig = px.box(
    df,
    x="Estacion",
    y=variable,
    color="Provincia",
    labels={variable: LABELS[variable], "Estacion": "Estación"},
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

# --- Promedios mensuales por estación ---
st.subheader(f"Promedio Mensual de {LABELS[variable]}")

df_copy = df.copy()
df_copy["Mes"] = df_copy["Date"].dt.month

monthly_avg = df_copy.groupby(["Mes", "Estacion"]).agg({variable: "mean"}).reset_index()

fig2 = px.line(
    monthly_avg,
    x="Mes",
    y=variable,
    color="Estacion",
    labels={variable: LABELS[variable], "Mes": "Mes", "Estacion": "Estación"},
    markers=True,
)
fig2.update_layout(height=420, xaxis=dict(dtick=1), legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig2, use_container_width=True)

# --- Tabla resumen ---
st.subheader("Resumen Estadístico")

summary = (
    df.groupby(["Provincia", "Estacion"])
    .agg(
        Promedio=(variable, "mean"),
        Mínimo=(variable, "min"),
        Máximo=(variable, "max"),
        Mediana=(variable, "median"),
        Desv_Std=(variable, "std"),
    )
    .round(1)
    .reset_index()
)
summary = summary.rename(columns={"Estacion": "Estación", "Desv_Std": "Desv. Estándar"})

st.dataframe(summary, use_container_width=True, hide_index=True)
