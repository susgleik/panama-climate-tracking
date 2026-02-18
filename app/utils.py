import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "cleaned" / "main_dataset.csv"


@st.cache_data
def load_data():
    """Carga el dataset consolidado de las 4 estaciones de Panamá."""
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def get_stations(df):
    return df["Estacion"].unique().tolist()


LABELS = {
    "Tavg": "Temp. Promedio (°C)",
    "Tmax": "Temp. Máxima (°C)",
    "Tmin": "Temp. Mínima (°C)",
    "Prcp": "Precipitación (mm)",
    "Wspd": "Vel. Viento (km/h)",
}

MONTH_NAMES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
