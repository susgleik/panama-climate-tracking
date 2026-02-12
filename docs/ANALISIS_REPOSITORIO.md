# Análisis del Repositorio: Panama Climate Tracking

## Descripción General

Proyecto de análisis climático que recopila, limpia, transforma y visualiza datos meteorológicos diarios del año 2024 para **8 estaciones** distribuidas en **3 países** de Centroamérica y Sudamérica: Panamá, Colombia y Costa Rica.

Implementa un pipeline ETL completo que va desde la extracción de datos crudos (API, web scraping, CSV) hasta un data warehouse con modelo estrella en SQLite, culminando en un dashboard interactivo en Power BI.

---

## Estructura del Proyecto

```
panama-climate-tracking/
│
├── datos_crudos/                    # Datos crudos sin procesar
│   ├── datos_bocas_del_toro_crudos_2024.json    (Meteostat API - JSON)
│   ├── datos_chiriqui_crudos_2024.csv           (Web Scraping IMHPA)
│   ├── datos_santiago_crudos_2024.xml           (Meteostat API - XML)
│   ├── datos_tocumen_crudos_2024.csv            (Meteostat Export - CSV)
│   ├── Ibague-co.csv                            (Colombia - Meteostat)
│   ├── Neiva-co.csv                             (Colombia - Meteostat)
│   ├── JuanSantamaria-cr.csv                    (Costa Rica - Meteostat)
│   └── PuertoLimon-cr.csv                       (Costa Rica - Meteostat)
│
├── datos_limpios/                   # Datos limpios y normalizados
│   ├── datos_limpios_bocas_del_toro_2024.csv
│   ├── datos_limpios_chiriqui_2024.csv
│   ├── datos_limpios_santiago_2024.csv
│   ├── datos_limpios_tocumen_2024.csv
│   ├── datos_limpios_ibague_2024.csv
│   ├── datos_limpios_juan_santamaria_2024.csv
│   ├── datos_limpios_neiva_2024.csv
│   ├── datos_limpios_puerto_limon_2024.csv
│   ├── main_dataset.csv                         (Consolidado Panamá)
│   └── main_dataset_pa.csv                      (Consolidado 3 países)
│
├── ET/                              # Notebooks de Extracción y Transformación
│   ├── json_bocas_del_toro.ipynb       (Extracción desde Meteostat API)
│   ├── xml_santiago.ipynb              (Extracción desde Meteostat API)
│   ├── web_scraping_chiriqui.ipynb     (Scraping del sitio IMHPA)
│   ├── csv_tocumen.ipynb               (Procesamiento CSV Meteostat)
│   ├── csv_ibague.ipynb                (Procesamiento Colombia)
│   ├── csv_neiva.ipynb                 (Procesamiento Colombia)
│   ├── csv_JuanSantamaria.ipynb        (Procesamiento Costa Rica)
│   ├── csv_PuertoLimon.ipynb           (Procesamiento Costa Rica)
│   └── database.ipynb                  (Carga al modelo estrella SQLite)
│
├── star_model/                      # Tablas del modelo estrella exportadas
│   ├── dim_pais.csv                    (3 registros - dimensión país)
│   ├── dim_estacion.csv                (8 registros - dimensión estación)
│   ├── dim_tiempo.csv                  (366 registros - dimensión tiempo)
│   └── hechos_clima.csv                (2,928 registros - tabla de hechos)
│
├── Limpieza_bocas_del_toro.ipynb    # Limpieza de datos JSON
├── Limpieza_santiago.ipynb          # Limpieza de datos XML
├── cleanner.ipynb                   # Operaciones generales de limpieza
├── sourceDoc.ipynb                  # Documentación de fuentes
│
├── weather.db                       # Base de datos SQLite (220 KB)
├── ClimateTracking2024.pbix         # Dashboard Power BI (8.9 MB)
└── README.md                        # Descripción del proyecto
```

---

## Tecnologías Utilizadas

| Categoría | Tecnología | Uso |
|-----------|------------|-----|
| Lenguaje | Python 3 | Procesamiento de datos y ETL |
| Manipulación de datos | pandas, NumPy | Limpieza, transformación, análisis |
| Extracción web | BeautifulSoup, requests | Web scraping de IMHPA |
| API climática | meteostat | Datos históricos meteorológicos |
| Base de datos | SQLite 3 | Almacenamiento del data warehouse |
| Visualización | Power BI | Dashboard interactivo |
| Notebooks | Jupyter Notebook | Desarrollo y documentación |
| Control de versiones | Git | Gestión del código |

---

## Fuentes de Datos

### 1. Meteostat API (Python Library)
- **Bocas del Toro**: Coordenadas (9.34°N, -82.24°W), formato JSON
- **Santiago**: Coordenadas (8.10°N, -80.98°W), formato XML
- **Tocumen**: Exportación directa en CSV

### 2. Web Scraping - IMHPA
- **Sitio**: https://www.imhpa.gob.pa/es/datos-diarios
- **Estaciones**: David (Chiriquí), Tocumen
- **Método**: BeautifulSoup parseando tablas HTML

### 3. Exportaciones CSV (Meteostat)
- Ibagué y Neiva (Colombia)
- Juan Santamaría y Puerto Limón (Costa Rica)

---

## Estaciones Meteorológicas

| # | Estación | Provincia | País | Latitud | Longitud |
|---|----------|-----------|------|---------|----------|
| 1 | La Cabaña | Bocas del Toro | Panamá | 9.34°N | 82.24°W |
| 2 | David | Chiriquí | Panamá | 8.43°N | 83.43°W |
| 3 | Santiago | Veraguas | Panamá | 8.10°N | 80.98°W |
| 4 | Tocumen | Panamá | Panamá | 9.09°N | 79.38°W |
| 5 | Ibagué | Tolima | Colombia | 4.44°N | 75.23°W |
| 6 | Neiva | Huila | Colombia | 2.94°N | 75.28°W |
| 7 | Juan Santamaría | Alajuela | Costa Rica | 10.59°N | 84.95°W |
| 8 | Puerto Limón | Limón | Costa Rica | 10.01°N | 83.04°W |

---

## Modelo de Datos (Esquema Estrella)

### Tabla de Hechos: `hechos_clima`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id_hecho | INTEGER PK | Identificador único |
| fecha_id | TEXT FK | Referencia a dim_tiempo |
| estacion_id | INTEGER FK | Referencia a dim_estacion |
| wdir_id | INTEGER FK | Referencia a dim_direccion_viento |
| tmax | REAL | Temperatura máxima (°C) |
| tmin | REAL | Temperatura mínima (°C) |
| tavg | REAL | Temperatura promedio (°C) |
| prcp | REAL | Precipitación (mm) |
| wspd | REAL | Velocidad del viento (km/h) |

**Total de registros**: 2,928 (8 estaciones × 366 días)

### Dimensiones

- **dim_tiempo** (366 registros): fecha, año, mes, día, nombre_mes, trimestre
- **dim_estacion** (8 registros): nombre, provincia, latitud, longitud
- **dim_direccion_viento**: Norte, Noreste, Este, Sureste, Sur, Suroeste, Oeste, Noroeste, Calmo
- **dim_pais** (3 registros): Panamá, Colombia, Costa Rica

---

## Pipeline ETL

```
┌─────────────────────────────────────────────────────────┐
│                    EXTRACCIÓN                           │
│  Meteostat API (JSON/XML) │ Web Scraping │ CSV Export   │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  TRANSFORMACIÓN                          │
│  1. Reemplazo de nulos ("", "-", "NA", "N/A" → NaN)    │
│  2. Conversión de tipos (string → float64)              │
│  3. Imputación: media (temperaturas), 0 (precipitación) │
│  4. Conversión de unidades (m/s → km/h)                 │
│  5. Normalización de dirección del viento (° → cardinal) │
│  6. Estandarización de nombres de columnas              │
│  7. Redondeo a 1 decimal                                │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                      CARGA                              │
│  SQLite (weather.db) → Modelo Estrella                  │
│  Exportación a CSV (star_model/)                        │
│  Dashboard Power BI (ClimateTracking2024.pbix)          │
└─────────────────────────────────────────────────────────┘
```

---

## Proceso de Limpieza de Datos

Cada estación pasa por un proceso estandarizado:

1. **Detección de nulos**: Identificación de valores faltantes (`NaN`, `"-"`, `"NA"`, `"N/A"`)
2. **Conversión numérica**: Columnas de texto a `float64`
3. **Imputación de temperaturas**: Valores faltantes reemplazados por la media de la columna
4. **Imputación de precipitación**: Valores faltantes reemplazados por 0 (se asume que no llovió)
5. **Imputación de velocidad de viento**: Valores faltantes reemplazados por la media
6. **Dirección del viento**: Valores faltantes reemplazados por la moda; grados convertidos a 8 puntos cardinales
7. **Redondeo**: Todos los valores numéricos redondeados a 1 decimal

### Calidad de Datos por Estación

| Estación | Registros | % Datos Faltantes |
|----------|-----------|-------------------|
| Bocas del Toro | 366 | 12.4% |
| Chiriquí | 334 | 11.34% |
| Santiago | 366 | 3.55% |
| Tocumen | 366 | ~3% |
| Ibagué | 366 | Variable |
| Neiva | 366 | Variable |
| Juan Santamaría | 366 | Variable |
| Puerto Limón | 366 | Variable |

---

## Variables Climáticas Registradas

| Variable | Unidad | Descripción |
|----------|--------|-------------|
| Tmax | °C | Temperatura máxima diaria |
| Tmin | °C | Temperatura mínima diaria |
| Tavg | °C | Temperatura promedio diaria |
| Prcp | mm | Precipitación diaria |
| Wspd | km/h | Velocidad del viento |
| Wdir | Cardinal | Dirección del viento (8 puntos) |

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Total de notebooks | 13 (9 ETL + 2 limpieza + 2 documentación) |
| Estaciones monitoreadas | 8 |
| Países cubiertos | 3 |
| Período de datos | 2024 completo (366 días, año bisiesto) |
| Registros en data warehouse | 2,928 |
| Tamaño de la base de datos | 220 KB |
| Tamaño total del proyecto | ~9.1 MB |
| Formatos de datos procesados | JSON, XML, CSV, HTML (web scraping) |
