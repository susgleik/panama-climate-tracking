# ⛅ Climate Tracking Panamá 2024

Pipeline ETL completo para datos meteorológicos de 4 estaciones en Panamá (2024). Extrae datos desde múltiples fuentes, los limpia y normaliza, los carga en un data warehouse SQLite con modelo estrella, y los visualiza en un dashboard interactivo.

## Estaciones Meteorológicas

| Estación | Provincia | Fuente |
|----------|-----------|--------|
| La Cabaña | Bocas del Toro | Meteostat API (JSON) |
| David | Chiriquí | Web scraping IMHPA |
| Santiago | Veraguas | Meteostat API (XML) |
| Tocumen | Panamá | Meteostat CSV |

## Stack

- **ETL**: Python, pandas, NumPy, BeautifulSoup, Meteostat
- **Data Warehouse**: SQLite (modelo estrella)
- **Visualización**: Streamlit + Plotly, Power BI
- **Infraestructura**: Docker, Jupyter Lab

## Estructura del Proyecto

```
data/
  raw/               → Datos crudos (JSON, XML, CSV, HTML)
  cleaned/           → Datos limpios y estandarizados
  warehouse/         → Tablas del modelo estrella (CSV)
database/            → weather.db (SQLite)
notebooks/
  extraction/        → Notebooks de extracción y transformación
  cleaning/          → Notebooks de limpieza
  analysis/          → Documentación de fuentes
app/                 → Dashboard Streamlit
dashboards/          → Dashboard Power BI (.pbix)
docs/                → Documentación detallada
```

## Inicio Rápido

### Requisitos

- Python 3.10+
- Dependencias en `requirements.txt`

### Instalación

```bash
git clone https://github.com/susgleik/panama-climate-tracking.git
cd panama-climate-tracking
pip install -r requirements.txt
```

### Ejecutar el Dashboard

```bash
streamlit run app/app.py
```

### Con Docker

```bash
docker-compose up
```

Esto levanta dos servicios:
- **Jupyter Lab** en `localhost:8888`
- **Streamlit** en `localhost:8501`

## Dashboard

El dashboard de Streamlit incluye 4 vistas:

- **Inicio** — Métricas generales, filtros por estación y fecha, gráficos de temperatura y precipitación
- **Por Estación** — Análisis individual con temperatura, precipitación mensual y dirección del viento
- **Comparativa** — Boxplots, promedios mensuales y resumen estadístico entre estaciones
- **Precipitación** — Totales anuales, mapa de calor mensual y distribución de días con lluvia

## Documentación

- [Análisis del repositorio](docs/ANALISIS_REPOSITORIO.md)
- [Mejoras propuestas](docs/MEJORAS.md)
- [Guía de Streamlit](docs/GUIA_STREAMLIT.md)
- [Cómo construí este proyecto](como-construi-panama-climate-tracking.md)
