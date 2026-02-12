# Mejoras Propuestas: Panama Climate Tracking

## Resumen

Este documento identifica áreas de mejora del proyecto agrupadas en categorías: estructura, calidad de código, datos, infraestructura, visualización y funcionalidades nuevas.

---

## 1. Estructura y Organización del Proyecto

### 1.1 Reorganizar la estructura de carpetas
**Problema**: Los notebooks de limpieza (`Limpieza_bocas_del_toro.ipynb`, `Limpieza_santiago.ipynb`, `cleanner.ipynb`) están en la raíz del proyecto mezclados con archivos de documentación y la base de datos.

**Mejora propuesta**:
```
panama-climate-tracking/
├── data/
│   ├── raw/                    # (antes datos_crudos/)
│   ├── cleaned/                # (antes datos_limpios/)
│   └── warehouse/              # (antes star_model/)
├── notebooks/
│   ├── extraction/             # Notebooks de extracción (antes ET/)
│   ├── cleaning/               # Notebooks de limpieza (ahora en raíz)
│   └── analysis/               # Notebooks de análisis y documentación
├── src/                        # Scripts Python reutilizables
│   ├── extractors/
│   ├── cleaners/
│   └── loaders/
├── config/                     # Archivos de configuración
├── tests/                      # Tests unitarios
├── dashboards/                 # Power BI y otros dashboards
├── database/
│   └── weather.db
├── requirements.txt
├── .gitignore
└── README.md
```

### 1.2 Agregar archivo `requirements.txt`
**Problema**: No existe un archivo de dependencias. Cualquier persona que clone el repo no sabrá qué paquetes instalar.

**Mejora propuesta**: Crear `requirements.txt`:
```
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
beautifulsoup4>=4.12.0
meteostat>=1.6.0
jupyter>=1.0.0
```

### 1.3 Agregar `.gitignore`
**Problema**: No existe un `.gitignore`. Archivos como `weather.db`, `.ipynb_checkpoints/`, `__pycache__/` y el `.pbix` (8.9 MB) podrían excluirse o manejarse con Git LFS.

**Mejora propuesta**:
```gitignore
__pycache__/
.ipynb_checkpoints/
*.pyc
.env
*.db           # O usar Git LFS para la base de datos
```

---

## 2. Calidad y Mantenibilidad del Código

### 2.1 Eliminar código duplicado en notebooks de limpieza
**Problema**: Cada notebook de limpieza repite la misma lógica (detección de nulos, imputación por media, redondeo, conversión de unidades). Hay al menos 8 notebooks con lógica casi idéntica.

**Mejora propuesta**: Crear un módulo Python reutilizable:
```python
# src/cleaners/climate_cleaner.py

class ClimateDataCleaner:
    def __init__(self, df, station_name, province):
        self.df = df
        self.station = station_name
        self.province = province

    def replace_nulls(self):
        """Reemplazar marcadores de nulos estándar."""
        ...

    def impute_temperatures(self, strategy='mean'):
        """Imputar temperaturas faltantes."""
        ...

    def convert_wind_speed(self, from_unit='m/s', to_unit='km/h'):
        """Convertir unidades de velocidad del viento."""
        ...

    def normalize_wind_direction(self):
        """Convertir grados a dirección cardinal."""
        ...

    def clean(self):
        """Ejecutar pipeline completo de limpieza."""
        ...
```

### 2.2 Extraer configuración hardcodeada
**Problema**: Coordenadas geográficas, nombres de estaciones, rutas de archivos y mapeos de columnas están hardcodeados directamente en los notebooks.

**Mejora propuesta**: Crear un archivo de configuración centralizado:
```python
# config/stations.py
STATIONS = {
    "bocas_del_toro": {
        "name": "La Cabaña",
        "province": "Bocas del Toro",
        "country": "Panama",
        "lat": 9.3400,
        "lon": -82.2400,
        "elevation": 11,
        "source": "meteostat_api",
        "raw_format": "json"
    },
    # ...
}
```

O usar un archivo YAML/JSON:
```yaml
# config/stations.yaml
stations:
  bocas_del_toro:
    name: "La Cabaña"
    province: "Bocas del Toro"
    country: "Panama"
    coordinates: [9.3400, -82.2400]
    elevation: 11
```

### 2.3 Convertir notebooks críticos a scripts Python
**Problema**: El pipeline ETL depende completamente de notebooks Jupyter, lo cual dificulta la automatización y reproducibilidad.

**Mejora propuesta**: Mantener los notebooks para exploración y documentación, pero crear scripts `.py` para el pipeline de producción:
```
src/
├── extract.py      # Extrae datos de todas las fuentes
├── clean.py        # Limpia todos los datasets
├── load.py         # Carga al data warehouse
└── pipeline.py     # Orquesta todo el ETL
```

Esto permitiría ejecutar: `python src/pipeline.py --year 2024`

---

## 3. Calidad de Datos

### 3.1 Mejorar la imputación de dirección del viento
**Problema**: Varias estaciones (Ibagué, Neiva, Juan Santamaría, Puerto Limón) tienen la dirección del viento asignada manualmente por rangos de fechas fijos, lo cual es una simplificación excesiva. Puerto Limón tiene "Norte" para todo el año.

**Mejora propuesta**:
- Utilizar datos de reanálisis (ERA5) para obtener direcciones de viento más precisas
- Implementar interpolación basada en estaciones cercanas que sí tienen datos
- Si se mantiene la asignación manual, documentar las fuentes meteorológicas que justifican los patrones estacionales

### 3.2 Datos faltantes en Chiriquí (Octubre)
**Problema**: La estación de Chiriquí tiene solo 334 registros (faltó el mes de octubre completo) debido a un error de conexión con el sitio IMHPA que no fue manejado.

**Mejora propuesta**:
- Implementar reintentos automáticos (`retry`) en el web scraping
- Agregar fallback a fuentes alternativas (Meteostat) cuando IMHPA no responde
- Registrar en un log qué meses/estaciones fallaron
- Considerar completar los datos faltantes desde otra fuente

### 3.3 Validación de datos post-limpieza
**Problema**: No existe un paso formal de validación después de la limpieza. Solo se usan `df.head()` y conteos manuales.

**Mejora propuesta**: Implementar validaciones automáticas:
```python
def validate_climate_data(df):
    assert df['Tmax'].between(-10, 50).all(), "Tmax fuera de rango"
    assert df['Tmin'].between(-15, 45).all(), "Tmin fuera de rango"
    assert (df['Tmax'] >= df['Tmin']).all(), "Tmax < Tmin detectado"
    assert df['Prcp'].ge(0).all(), "Precipitación negativa detectada"
    assert df['Wspd'].ge(0).all(), "Velocidad de viento negativa"
    assert df.isna().sum().sum() == 0, "Valores nulos restantes"
    assert len(df) == 366, f"Se esperaban 366 filas, se encontraron {len(df)}"
```

### 3.4 Documentar el linaje de datos (Data Lineage)
**Problema**: No hay trazabilidad clara de qué transformaciones se aplicaron a cada dato y cuáles valores son originales vs. imputados.

**Mejora propuesta**: Agregar columnas de metadatos:
- `is_imputed_tmax`, `is_imputed_prcp`, etc. (booleanos indicando si el valor fue imputado)
- O mantener un log CSV separado con las transformaciones aplicadas por registro

---

## 4. Base de Datos y Modelo

### 4.1 Corregir tipos de datos en el esquema
**Problema**: La columna `fecha_id` en `hechos_clima` es de tipo `TEXT` cuando debería ser `INTEGER` para ser consistente con la PK de `dim_tiempo`.

**Mejora propuesta**: Cambiar a `INTEGER` y agregar restricciones de integridad referencial:
```sql
CREATE TABLE hechos_clima (
    id_hecho INTEGER PRIMARY KEY,
    fecha_id INTEGER NOT NULL REFERENCES dim_tiempo(fecha_id),
    estacion_id INTEGER NOT NULL REFERENCES dim_estacion(estacion_id),
    wdir_id INTEGER NOT NULL REFERENCES dim_direccion_viento(wdir_id),
    ...
);
```

### 4.2 Agregar la dimensión país como FK en estaciones
**Problema**: Existe `dim_pais` pero no se conecta formalmente a `dim_estacion` mediante foreign key.

**Mejora propuesta**: Agregar `pais_id` a `dim_estacion`:
```sql
ALTER TABLE dim_estacion ADD COLUMN pais_id INTEGER REFERENCES dim_pais(pais_id);
```

### 4.3 Considerar migración a PostgreSQL
**Problema**: SQLite es limitado para análisis concurrente, consultas complejas y escalabilidad.

**Mejora propuesta**: Si el proyecto crece (más años, más estaciones), migrar a PostgreSQL con extensión PostGIS para consultas geoespaciales:
```sql
-- Ejemplo con PostGIS
SELECT e.nombre_estacion, AVG(h.tavg)
FROM hechos_clima h
JOIN dim_estacion e ON h.estacion_id = e.estacion_id
WHERE ST_DWithin(e.geom, ST_MakePoint(-79.5, 9.0)::geography, 100000)
GROUP BY e.nombre_estacion;
```

---

## 5. Testing y CI/CD

### 5.1 Agregar tests unitarios
**Problema**: No existe ningún test automatizado en el proyecto.

**Mejora propuesta**: Crear tests con `pytest`:
```python
# tests/test_cleaning.py
def test_temperature_imputation():
    """Verificar que no quedan nulos después de imputar."""
    ...

def test_wind_direction_conversion():
    """Verificar conversión de grados a cardinal."""
    assert degrees_to_cardinal(0) == "Norte"
    assert degrees_to_cardinal(90) == "Este"
    assert degrees_to_cardinal(225) == "Suroeste"

def test_wind_speed_conversion():
    """Verificar conversión m/s a km/h."""
    assert round(10 * 3.6, 1) == 36.0

def test_data_completeness():
    """Verificar que cada estación tiene 366 registros."""
    ...
```

### 5.2 Implementar CI/CD básico
**Mejora propuesta**: Agregar GitHub Actions para:
- Ejecutar tests automáticamente en cada push
- Validar la integridad de los datos limpios
- Ejecutar el pipeline ETL completo como verificación

---

## 6. Visualización y Reportes

### 6.1 Agregar visualizaciones en Python
**Problema**: Las visualizaciones dependen exclusivamente de Power BI, que requiere licencia y es solo para Windows.

**Mejora propuesta**: Crear visualizaciones complementarias con matplotlib/seaborn/plotly:
```python
# notebooks/analysis/climate_visualizations.ipynb
import plotly.express as px

# Mapa interactivo de estaciones
fig = px.scatter_mapbox(stations_df, lat="latitud", lon="longitud",
                         color="pais", size="avg_temp",
                         hover_name="nombre_estacion")

# Series temporales comparativas
fig = px.line(climate_df, x="Date", y="Tavg",
              color="Estacion", title="Temperatura Promedio 2024")
```

### 6.2 Dashboard web interactivo
**Mejora propuesta**: Crear un dashboard con Streamlit o Dash como alternativa accesible al Power BI:
```python
# app.py
import streamlit as st
import pandas as pd

st.title("Panama Climate Tracking 2024")
station = st.selectbox("Seleccionar estación", stations)
metric = st.selectbox("Variable", ["Tmax", "Tmin", "Tavg", "Prcp", "Wspd"])
# ... gráficos interactivos
```

### 6.3 Exportar imágenes del dashboard Power BI
**Problema**: El dashboard solo es visible si se tiene Power BI Desktop instalado.

**Mejora propuesta**: Incluir capturas de pantalla o exportar las visualizaciones clave como imágenes en una carpeta `docs/images/` para que sean accesibles en el README.

---

## 7. Nuevas Funcionalidades

### 7.1 Soporte multi-año
**Problema**: Todo está hardcodeado para el año 2024.

**Mejora propuesta**: Parametrizar el año para permitir análisis históricos:
```python
def extract_data(station, year=2024):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    ...
```

### 7.2 Agregar más variables climáticas
**Mejora propuesta**: Incluir variables adicionales disponibles en Meteostat:
- **Humedad relativa** (%)
- **Presión atmosférica** (hPa)
- **Cobertura de nubes** (oktas)
- **Visibilidad** (km)
- **Índice UV**

### 7.3 Análisis estadístico avanzado
**Mejora propuesta**: Agregar notebooks de análisis que incluyan:
- **Correlaciones** entre variables (temperatura vs. precipitación)
- **Anomalías climáticas**: Identificar días atípicos por estación
- **Tendencias estacionales**: Análisis por trimestre/mes
- **Comparación regional**: Análisis estadístico entre países
- **Promedios móviles**: Suavizar series temporales (7, 14, 30 días)

### 7.4 Alertas de datos anómalos
**Mejora propuesta**: Implementar detección automática de outliers:
```python
from scipy import stats

def detect_anomalies(df, column, z_threshold=3):
    z_scores = stats.zscore(df[column].dropna())
    return df[abs(z_scores) > z_threshold]
```

### 7.5 API REST para consultar los datos
**Mejora propuesta**: Crear una API con FastAPI para exponer los datos:
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/climate/{station}")
def get_climate(station: str, start_date: str, end_date: str):
    ...

@app.get("/api/stations")
def list_stations():
    ...
```

---

## 8. Documentación

### 8.1 Mejorar el README.md
**Problema**: El README actual es básico y no incluye instrucciones claras de instalación o ejecución.

**Mejora propuesta**: Incluir:
- Instrucciones paso a paso de instalación
- Cómo ejecutar el pipeline completo
- Descripción del modelo de datos con diagrama
- Capturas del dashboard
- Licencia del proyecto
- Sección de contribución

### 8.2 Documentar las decisiones de diseño
**Mejora propuesta**: Crear un archivo `DECISIONS.md` que documente:
- Por qué se eligió el modelo estrella
- Criterios de selección de estaciones
- Justificación de las estrategias de imputación
- Por qué se incluyeron Colombia y Costa Rica

### 8.3 Agregar docstrings a funciones
**Problema**: Los notebooks no tienen documentación en las funciones/celdas.

**Mejora propuesta**: Agregar docstrings claros que expliquen entradas, salidas y lógica.

---

## 9. Seguridad y Buenas Prácticas

### 9.1 No almacenar la base de datos en el repo
**Problema**: `weather.db` (220 KB) está directamente en el repositorio. Si crece, esto inflará el historial de Git.

**Mejora propuesta**: Incluir un script de regeneración en vez de almacenar la DB:
```bash
# Regenerar la base de datos desde los datos limpios
python src/load.py --rebuild
```

### 9.2 Manejo de errores en web scraping
**Problema**: El scraping de IMHPA no tiene manejo robusto de errores (el mes de octubre de Chiriquí se perdió por un error de conexión).

**Mejora propuesta**:
```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503])
session.mount('https://', HTTPAdapter(max_retries=retry))
```

---

## Resumen de Prioridades

| Prioridad | Mejora | Impacto | Esfuerzo |
|-----------|--------|---------|----------|
| Alta | Agregar `requirements.txt` y `.gitignore` | Alto | Bajo |
| Alta | Eliminar código duplicado (módulo de limpieza) | Alto | Medio |
| Alta | Completar datos faltantes de Chiriquí | Alto | Bajo |
| Alta | Agregar validación post-limpieza | Alto | Bajo |
| Media | Extraer configuración hardcodeada | Medio | Bajo |
| Media | Corregir tipos en el esquema de DB | Medio | Bajo |
| Media | Agregar tests unitarios | Alto | Medio |
| Media | Mejorar el README.md | Medio | Bajo |
| Media | Agregar visualizaciones Python | Medio | Medio |
| Baja | Convertir notebooks a scripts | Medio | Alto |
| Baja | Crear dashboard web (Streamlit) | Alto | Alto |
| Baja | Soporte multi-año | Medio | Medio |
| Baja | API REST con FastAPI | Medio | Alto |
| Baja | Migración a PostgreSQL | Bajo | Alto |
