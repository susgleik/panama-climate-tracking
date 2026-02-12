# Guía de Implementación: Dashboard con Streamlit

## Qué es Streamlit

Streamlit es una librería de Python que convierte scripts de datos en aplicaciones web interactivas. No necesitas saber HTML, CSS ni JavaScript. Si sabes pandas, ya sabes el 80% de lo que necesitas.

---

## Paso 1: Preparar el Entorno

### 1.1 Crear un entorno virtual

```bash
# En la raíz del proyecto
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate
```

### 1.2 Instalar dependencias

```bash
pip install streamlit pandas plotly
```

> **plotly** es opcional pero recomendado. Genera gráficos interactivos (zoom, hover, filtros) que se integran perfectamente con Streamlit.

### 1.3 Verificar instalación

```bash
streamlit hello
```

Esto abrirá una demo en tu navegador (`http://localhost:8501`). Si carga, todo está listo.

---

## Paso 2: Estructura de Archivos

Crear la siguiente estructura dentro del proyecto:

```
panama-climate-tracking/
├── app/
│   ├── app.py                  # Archivo principal de Streamlit
│   ├── pages/                  # Páginas adicionales (navegación automática)
│   │   ├── 1_Por_Estacion.py
│   │   ├── 2_Comparativa.py
│   │   └── 3_Precipitacion.py
│   └── utils.py                # Funciones auxiliares (carga de datos, etc.)
├── datos_limpios/
│   └── main_dataset_pa.csv     # Dataset principal (ya existe)
└── ...
```

> Streamlit detecta automáticamente la carpeta `pages/` y crea una barra lateral de navegación con cada archivo `.py` que esté dentro.

---

## Paso 3: Código Base

### 3.1 Funciones auxiliares — `app/utils.py`

```python
import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """
    Carga el dataset principal.
    @st.cache_data evita recargar el CSV en cada interacción del usuario.
    """
    df = pd.read_csv("datos_limpios/main_dataset_pa.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def get_stations(df):
    """Retorna lista única de estaciones."""
    return df["Estacion"].unique().tolist()


def get_countries(df):
    """Retorna lista única de países."""
    return df["País"].unique().tolist()


def filter_by_station(df, station):
    """Filtra el dataframe por estación."""
    return df[df["Estacion"] == station]


def filter_by_date_range(df, start, end):
    """Filtra el dataframe por rango de fechas."""
    return df[(df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))]
```

### 3.2 Página principal — `app/app.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, get_stations, get_countries

# --- Configuración de la página ---
st.set_page_config(
    page_title="Climate Tracking Panamá 2024",
    page_icon="🌤️",
    layout="wide"
)

# --- Cargar datos ---
df = load_data()

# --- Encabezado ---
st.title("Climate Tracking 2024")
st.markdown("Dashboard climático de Panamá, Colombia y Costa Rica")

# --- Métricas generales (fila de tarjetas) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Estaciones", df["Estacion"].nunique())
col2.metric("Países", df["País"].nunique())
col3.metric("Registros", f"{len(df):,}")
col4.metric("Temp. Promedio", f"{df['Tavg'].mean():.1f} °C")

st.divider()

# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros")

country = st.sidebar.multiselect(
    "País",
    options=get_countries(df),
    default=get_countries(df)
)

filtered = df[df["País"].isin(country)]

station = st.sidebar.multiselect(
    "Estación",
    options=filtered["Estacion"].unique().tolist(),
    default=filtered["Estacion"].unique().tolist()
)

filtered = filtered[filtered["Estacion"].isin(station)]

date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(df["Date"].min(), df["Date"].max()),
    min_value=df["Date"].min(),
    max_value=df["Date"].max()
)

if len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered["Date"] <= pd.to_datetime(date_range[1]))
    ]

# --- Gráfico: Temperatura promedio por estación ---
st.subheader("Temperatura Promedio Diaria")

fig_temp = px.line(
    filtered,
    x="Date",
    y="Tavg",
    color="Estacion",
    labels={"Tavg": "Temperatura (°C)", "Date": "Fecha"},
)
fig_temp.update_layout(height=400)
st.plotly_chart(fig_temp, use_container_width=True)

# --- Gráfico: Precipitación ---
st.subheader("Precipitación Diaria")

fig_prcp = px.bar(
    filtered,
    x="Date",
    y="Prcp",
    color="Estacion",
    labels={"Prcp": "Precipitación (mm)", "Date": "Fecha"},
)
fig_prcp.update_layout(height=400)
st.plotly_chart(fig_prcp, use_container_width=True)

# --- Tabla de datos ---
st.subheader("Datos")
st.dataframe(filtered, use_container_width=True, hide_index=True)
```

### 3.3 Página por estación — `app/pages/1_Por_Estacion.py`

```python
import streamlit as st
import plotly.express as px
from utils import load_data, get_stations

st.set_page_config(page_title="Por Estación", layout="wide")

df = load_data()

st.title("Análisis por Estación")

station = st.selectbox("Seleccionar estación", get_stations(df))
station_df = df[df["Estacion"] == station]

# Métricas de la estación seleccionada
col1, col2, col3, col4 = st.columns(4)
col1.metric("Temp. Máx. Registrada", f"{station_df['Tmax'].max():.1f} °C")
col2.metric("Temp. Mín. Registrada", f"{station_df['Tmin'].min():.1f} °C")
col3.metric("Precip. Total Anual", f"{station_df['Prcp'].sum():.1f} mm")
col4.metric("Vel. Viento Promedio", f"{station_df['Wspd'].mean():.1f} km/h")

# Gráfico de temperaturas (máx, mín, promedio)
fig = px.line(
    station_df,
    x="Date",
    y=["Tmax", "Tmin", "Tavg"],
    labels={"value": "Temperatura (°C)", "Date": "Fecha", "variable": "Variable"},
    title=f"Temperaturas — {station}"
)
st.plotly_chart(fig, use_container_width=True)

# Gráfico de precipitación mensual
station_df = station_df.copy()
station_df["Mes"] = station_df["Date"].dt.month_name()
monthly = station_df.groupby(station_df["Date"].dt.month).agg({"Prcp": "sum"}).reset_index()
monthly.columns = ["Mes", "Precipitación (mm)"]

fig2 = px.bar(monthly, x="Mes", y="Precipitación (mm)",
              title=f"Precipitación Mensual — {station}")
st.plotly_chart(fig2, use_container_width=True)
```

### 3.4 Página comparativa — `app/pages/2_Comparativa.py`

```python
import streamlit as st
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Comparativa", layout="wide")

df = load_data()

st.title("Comparativa entre Estaciones")

variable = st.selectbox("Variable a comparar", ["Tavg", "Tmax", "Tmin", "Prcp", "Wspd"])
labels = {
    "Tavg": "Temp. Promedio (°C)",
    "Tmax": "Temp. Máxima (°C)",
    "Tmin": "Temp. Mínima (°C)",
    "Prcp": "Precipitación (mm)",
    "Wspd": "Vel. Viento (km/h)"
}

# Boxplot comparativo
fig = px.box(df, x="Estacion", y=variable, color="País",
             labels={variable: labels[variable]},
             title=f"Distribución de {labels[variable]} por Estación")
st.plotly_chart(fig, use_container_width=True)

# Tabla resumen
summary = df.groupby(["País", "Estacion"]).agg(
    Promedio=(variable, "mean"),
    Mínimo=(variable, "min"),
    Máximo=(variable, "max"),
    Mediana=(variable, "median")
).round(1).reset_index()

st.dataframe(summary, use_container_width=True, hide_index=True)
```

---

## Paso 4: Ejecutar la Aplicación

```bash
# Desde la raíz del proyecto
cd app
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501`.

La barra lateral mostrará:
- **app** (página principal)
- **1 Por Estacion**
- **2 Comparativa**
- **3 Precipitacion**

---

## Paso 5: Despliegue Gratuito (Streamlit Community Cloud)

### 5.1 Preparar archivos para deploy

Crear `requirements.txt` en la raíz del proyecto:

```
streamlit
pandas
plotly
```

### 5.2 Subir a GitHub

```bash
git add .
git commit -m "Add Streamlit dashboard"
git push origin main
```

### 5.3 Desplegar

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Iniciar sesión con tu cuenta de GitHub
3. Click en **"New app"**
4. Seleccionar:
   - **Repositorio**: `panama-climate-tracking`
   - **Branch**: `main`
   - **Main file path**: `app/app.py`
5. Click en **"Deploy"**

En unos minutos tendrás una URL pública como:
```
https://tu-usuario-panama-climate-tracking.streamlit.app
```

---

## Paso 6: Personalización Visual (Opcional)

### 6.1 Tema personalizado

Crear archivo `.streamlit/config.toml` dentro de `app/`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 6.2 Logo y favicon

```python
st.set_page_config(
    page_title="Climate Tracking 2024",
    page_icon="🌤️",        # Aparece como favicon
    layout="wide",
    initial_sidebar_state="expanded"
)
```

---

## Componentes Útiles de Streamlit — Referencia Rápida

| Componente | Código | Para qué sirve |
|------------|--------|-----------------|
| Texto | `st.title()`, `st.header()`, `st.markdown()` | Encabezados y texto |
| Métricas | `st.metric("Label", value, delta)` | Tarjetas con KPIs |
| Tabla | `st.dataframe(df)` | Tabla interactiva con sort/filter |
| Gráfico Plotly | `st.plotly_chart(fig)` | Gráficos interactivos |
| Gráfico nativo | `st.line_chart(df)`, `st.bar_chart(df)` | Gráficos simples (sin Plotly) |
| Selector | `st.selectbox("Label", options)` | Dropdown de opciones |
| Multi-selector | `st.multiselect("Label", options)` | Selección múltiple |
| Slider | `st.slider("Label", min, max)` | Rango numérico |
| Fecha | `st.date_input("Label")` | Selector de fecha |
| Columnas | `st.columns(n)` | Layout en columnas |
| Sidebar | `st.sidebar.xxx()` | Elementos en barra lateral |
| Tabs | `st.tabs(["Tab1", "Tab2"])` | Pestañas |
| Descarga | `st.download_button()` | Botón para descargar archivos |
| Mapa | `st.map(df)` | Mapa con coordenadas |

---

## Resumen del Proceso

```
1. pip install streamlit pandas plotly
2. Crear app/app.py con el código
3. Crear páginas en app/pages/
4. streamlit run app/app.py → ver en localhost:8501
5. Subir a GitHub → Deploy en share.streamlit.io
```

Tiempo estimado hasta tener algo funcional: **2-4 horas** (incluyendo personalización).
