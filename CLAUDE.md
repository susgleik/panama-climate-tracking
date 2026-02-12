# CLAUDE.md — Contexto del Proyecto

## Descripción

Proyecto de análisis climático que implementa un pipeline ETL completo para datos meteorológicos del año 2024. Recopila datos de 8 estaciones en Panamá, Colombia y Costa Rica desde múltiples fuentes (Meteostat API, web scraping IMHPA, CSV), los limpia/normaliza, los carga en un data warehouse SQLite con modelo estrella, y los visualiza en Power BI.

## Estructura del Proyecto

```
datos_crudos/          → Datos crudos (JSON, XML, CSV, HTML scrapeado)
datos_limpios/         → Datos limpios y normalizados (CSV estandarizado)
ET/                    → Notebooks de extracción y transformación
star_model/            → Tablas del modelo estrella exportadas a CSV
weather.db             → Base de datos SQLite (modelo estrella)
ClimateTracking2024.pbix → Dashboard Power BI
```

Los notebooks de limpieza (`Limpieza_*.ipynb`, `cleanner.ipynb`) están en la raíz. `sourceDoc.ipynb` documenta las fuentes.

## Stack Tecnológico

- **Python 3** con pandas, NumPy, BeautifulSoup, requests, meteostat
- **SQLite 3** para el data warehouse
- **Jupyter Notebook** para ETL y análisis
- **Power BI** para visualización
- **Streamlit** planificado para dashboard web (ver `GUIA_STREAMLIT.md`)

## Esquema de la Base de Datos (SQLite — weather.db)

Modelo estrella con 4 dimensiones y 1 tabla de hechos:

- `dim_tiempo` (fecha_id PK, fecha, año, mes, día, nombre_mes, trimestre) — 366 registros
- `dim_estacion` (estacion_id PK, nombre_estacion, provincia, latitud, longitud) — 8 registros
- `dim_direccion_viento` (wdir_id PK, direccion_cardinal) — 9 direcciones
- `dim_pais` (pais_id PK, nombre_pais) — 3 registros
- `hechos_clima` (id_hecho PK, fecha_id FK, estacion_id FK, wdir_id FK, tmax, tmin, tavg, prcp, wspd) — 2,928 registros

**Nota**: `fecha_id` en `hechos_clima` es tipo TEXT (debería ser INTEGER). `dim_pais` no tiene FK hacia `dim_estacion`.

## Formato Estándar de Datos Limpios

Todos los CSV en `datos_limpios/` siguen este esquema:

```
Date       | Tmax (°C) | Tmin (°C) | Tavg (°C) | Prcp (mm) | Wspd (km/h) | Wdir (cardinal) | Estacion | Provincia
```

- 367 filas (header + 366 días del año bisiesto 2024)
- `main_dataset.csv` consolida las 4 estaciones de Panamá
- `main_dataset_pa.csv` consolida las 8 estaciones (3 países), incluye columna extra `País`

## Estaciones

| Estación | Provincia | País | Fuente |
|----------|-----------|------|--------|
| La Cabaña | Bocas del Toro | Panamá | Meteostat API (JSON) |
| David | Chiriquí | Panamá | Web scraping IMHPA |
| Santiago | Veraguas | Panamá | Meteostat API (XML) |
| Tocumen | Panamá | Panamá | Meteostat CSV export |
| Ibagué | Tolima | Colombia | Meteostat CSV |
| Neiva | Huila | Colombia | Meteostat CSV |
| Juan Santamaría | Alajuela | Costa Rica | Meteostat CSV |
| Puerto Limón | Limón | Costa Rica | Meteostat CSV |

## Pipeline de Limpieza (aplicado en cada notebook)

1. Reemplazar marcadores de nulos: `""`, `"-"`, `"NA"`, `"N/A"`, `"n/a"` → `NaN`
2. Convertir columnas a `float64` con `pd.to_numeric(errors='coerce')`
3. Imputar temperaturas con la **media** de la columna
4. Imputar precipitación con **0** (se asume no llovió)
5. Imputar velocidad de viento con la **media**
6. Imputar dirección de viento con la **moda**
7. Convertir velocidad de viento de m/s → km/h (`* 3.6`) si aplica
8. Convertir grados de viento → 8 puntos cardinales (Norte, Noreste, etc.)
9. Redondear todo a 1 decimal
10. Estandarizar nombres de columnas al formato inglés (Date, Tmax, Tmin, etc.)

## Convenciones del Código

### Nombrado
- **Variables y funciones**: camelCase en algunos notebooks (`datosTocumenCrudos`, `gradosAPuntoCardinal`), snake_case en otros (`columnas_estandar`, `data_total`). No hay consistencia — **preferir snake_case** para código nuevo (PEP 8).
- **Archivos CSV**: `datos_limpios_{estacion}_{año}.csv` para datos individuales
- **Notebooks**: `{formato}_{estacion}.ipynb` para ETL, `Limpieza_{estacion}.ipynb` para limpieza

### Patrones recurrentes en notebooks
```python
# Carga de datos
df = pd.read_csv("../datos_limpios/datos_limpios_{estacion}_2024.csv")

# Reemplazo de nulos
df.replace(["", "-", "NA", "N/A", "n/a"], np.nan, inplace=True)

# Mapeo de columnas al formato estándar
columnas_estandar = {
    'Fecha': 'Date',
    'Temperatura Máxima (°C)': 'Tmax',
    'Temperatura Mínima (°C)': 'Tmin',
    'Temperatura Promedio (°C)': 'Tavg',
    'Lluvia Mes Actual (mm)': 'Prcp',
    'Viento Velocidad Máxima (Km/h)': 'Wspd',
    'Dirección del Viento': 'Wdir'
}
df = df.rename(columns=columnas_estandar)
df = df[list(columnas_estandar.values())]

# Agregar metadatos de estación
df["Estacion"] = "NombreEstacion"
df["Provincia"] = "NombreProvincia"

# Guardar
df.to_csv("../datos_limpios/datos_limpios_{estacion}_2024.csv", index=False)
```

### Coordenadas hardcodeadas (en database.ipynb)
```python
points = {
    "Bocas del Toro": (9.3400, -82.2400, 11),
    "Veraguas": (8.1000, -80.9833, 90),
    "Panamá": (9.08939, -79.38310),
    "Chiriquí": (8.42729, -83.43085001)
}
```

## Problemas Conocidos

- **Chiriquí tiene solo 334 registros** (falta octubre completo por ConnectionResetError en IMHPA)
- **Dirección de viento muy imputada**: Bocas del Toro y Santiago tienen 100% faltante en wdir original; Colombia y Costa Rica usan asignación manual por rangos de fechas
- **`cleanner.ipynb` tiene un NameError**: llama a `analizar_limpieza` (con z) pero la función se define como `analizar_limpieaza` (typo con doble a)
- **No hay `requirements.txt`** ni `.gitignore`
- **No hay tests automatizados**

## Mejores Prácticas de Python para Este Proyecto

### Seguir PEP 8
- Usar **snake_case** para variables y funciones: `datos_tocumen`, `limpiar_datos()`
- Usar **PascalCase** solo para clases: `ClimateDataCleaner`
- Líneas de máximo 88-100 caracteres
- Imports al inicio del archivo, agrupados: stdlib → terceros → locales

### Evitar `inplace=True`
```python
# Evitar
df.replace(["", "-"], np.nan, inplace=True)

# Preferir
df = df.replace(["", "-"], np.nan)
```

### Usar f-strings en vez de concatenación
```python
# Evitar
path = output_dir + "/" + file

# Preferir
path = f"{output_dir}/{file}"
# O mejor: usar pathlib
from pathlib import Path
path = Path(output_dir) / file
```

### Usar `pathlib` en vez de `os.path`
```python
from pathlib import Path

data_dir = Path("../datos_limpios")
file_path = data_dir / f"datos_limpios_{station}_2024.csv"
```

### Usar context managers para archivos y conexiones
```python
# Ya se hace correctamente con sqlite3:
with sqlite3.connect("../weather.db") as conn:
    ...
```

### Tipado opcional (type hints)
```python
def degrees_to_cardinal(deg: float) -> str:
    directions = ["Norte", "Noreste", "Este", "Sureste",
                   "Sur", "Suroeste", "Oeste", "Noroeste"]
    ix = int((deg + 22.5) / 45) % 8
    return directions[ix]
```

## Archivos de Documentación

- `ANALISIS_REPOSITORIO.md` — Análisis completo de lo que contiene el repo
- `MEJORAS.md` — Propuestas de mejoras priorizadas
- `GUIA_STREAMLIT.md` — Guía paso a paso para implementar dashboard con Streamlit

## Al Modificar Este Proyecto

1. Respetar el formato CSV estándar de 9 columnas (Date, Tmax, Tmin, Tavg, Prcp, Wspd, Wdir, Estacion, Provincia)
2. Mantener las rutas relativas con `../` desde los notebooks en subcarpetas
3. Si se agrega una estación nueva, actualizar `points` en `database.ipynb` y re-ejecutar la carga
4. No modificar archivos en `datos_crudos/` — son datos fuente inmutables
5. Cualquier script nuevo en Python debe seguir snake_case (PEP 8)
6. Idioma del código: variables y funciones pueden estar en español o inglés, pero los nombres de columnas del CSV siempre en inglés (Date, Tmax, etc.)
