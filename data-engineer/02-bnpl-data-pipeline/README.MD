# 💳 BNPL Analytics Pipeline

## Proyecto 02 — Data Engineering & Data Analytics

Pipeline ETL desarrollado en **Python y Pandas** para procesar información
relacionada con operaciones **Buy Now Pay Later (BNPL)**, aplicar controles de
**Data Quality**, generar variables derivadas y almacenar los datos procesados
en **SQLite** para su posterior análisis mediante SQL.

Este proyecto representa el segundo nivel del portfolio de **Data Engineering**,
incorporando sobre el pipeline anterior una mayor cantidad de validaciones,
segmentaciones y métricas analíticas.

El flujo principal del proyecto es:

```text
Extract → Data Quality → Transform → Load → Analytics
```

---

## 🎯 Objetivo

Construir un pipeline capaz de:

- Extraer información desde un archivo CSV.
- Validar la estructura del dataset.
- Convertir y validar tipos de datos.
- Detectar registros duplicados.
- Identificar valores nulos.
- Validar rangos de edad.
- Validar ingresos.
- Validar montos de compra.
- Validar rangos de `Credit_Score`.
- Validar estados de pago.
- Generar variables derivadas.
- Segmentar clientes por edad.
- Segmentar clientes por nivel crediticio.
- Transformar los estados de pago.
- Almacenar los datos procesados en SQLite.
- Crear vistas SQL analíticas.
- Registrar el proceso mediante logging.
- Ejecutar el pipeline mediante Python o Docker.

---

# 🏗️ Arquitectura

```text
bnpl.csv
   │
   ▼
EXTRACT
   │
   ▼
DATA QUALITY
   │
   ├── Columnas requeridas
   ├── Conversión numérica
   ├── Duplicados
   ├── Valores nulos
   ├── Edad válida
   ├── Ingresos válidos
   ├── Purchase Amount válido
   ├── Credit Score válido
   ├── Repayment Status válido
   └── Transaction ID válido
   │
   ▼
TRANSFORM
   │
   ├── rango_edad
   ├── nivel_credito
   └── estado_pago
   │
   ▼
LOAD
   │
   ▼
SQLite
   │
   ├── v_riesgo_por_edad
   ├── v_riesgo_por_proveedor
   └── v_riesgo_por_categoria
   │
   ▼
SQL ANALYTICS
```

---

# 📂 Estructura del proyecto

```text
02-pipeline-bnpl/
│
├── data/
│   └── bnpl.csv
│
├── Dockerfile
├── docker-compose.yml
├── bnpl_pipeline.py
├── requirements.txt
└── README.MD
```

Durante la ejecución se generan archivos locales como:

```text
bnpl_analytics.db
registro_bnpl.log
```

Estos archivos son generados por el pipeline y se mantienen fuera del control
de versiones.

---

# 🔄 Pipeline ETL

## 1. Extract

El pipeline carga el dataset:

```text
data/bnpl.csv
```

utilizando **Pandas**.

Antes de comenzar el procesamiento se verifica que el archivo exista.

El pipeline registra mediante logging la cantidad de registros extraídos.

En la ejecución utilizada para documentar este proyecto se procesaron:

```text
50,000 registros
```

---

# 🧪 2. Data Quality

La etapa de Data Quality permite validar que los datos cumplan las condiciones
necesarias antes de almacenarlos.

## Columnas requeridas

El pipeline verifica la existencia de las siguientes columnas:

```text
Transaction_ID
Customer_Age
Gender
Annual_Income
Credit_Score
Purchase_Category
BNPL_Provider
Purchase_Amount
Repayment_Status
```

Si falta alguna columna requerida, el proceso genera un error.

---

## Conversión de datos numéricos

Las siguientes columnas son convertidas a valores numéricos antes de realizar
las validaciones:

```text
Customer_Age
Annual_Income
Credit_Score
Purchase_Amount
```

Esto permite detectar valores que no puedan ser utilizados correctamente en
las operaciones posteriores.

---

## Duplicados

Se verifica la existencia de registros duplicados utilizando:

```text
Transaction_ID
```

Los registros duplicados son eliminados conservando la primera aparición.

---

## Valores nulos

Se verifican valores nulos en el dataset y se eliminan los registros que no
puedan continuar correctamente hacia las etapas posteriores.

---

## Edad

Se valida que:

```text
18 ≤ Customer_Age ≤ 64
```

Los registros fuera de este rango son considerados inválidos.

---

## Ingresos

Se valida que:

```text
Annual_Income > 0
```

Los ingresos menores o iguales a cero son considerados inválidos.

---

## Monto de compra

Se valida que:

```text
Purchase_Amount > 0
```

Los montos menores o iguales a cero son considerados inválidos.

---

## Credit Score

El pipeline valida que el puntaje crediticio se encuentre dentro del rango:

```text
300 ≤ Credit_Score ≤ 849
```

Los valores fuera de este rango son considerados inválidos.

---

## Estado de pago

El campo:

```text
Repayment_Status
```

debe contener uno de los siguientes valores:

```text
Paid On Time
Late Payment
Defaulted
```

Los valores diferentes son considerados inválidos.

---

## Identificador de transacción

Los identificadores vacíos también son descartados.

---

# 🧮 3. Feature Engineering

Una vez completadas las validaciones, el pipeline genera variables adicionales
para facilitar el análisis.

---

## Rango de edad

La edad de los clientes se transforma en segmentos:

| Rango | Segmento |
|---|---|
| 18 – 25 | Joven |
| 26 – 40 | Adulto Joven |
| 41 – 60 | Adulto |
| > 60 | Senior |

La variable generada es:

```text
rango_edad
```

---

## Nivel crediticio

El `Credit_Score` se transforma en segmentos analíticos:

| Credit Score | Nivel |
|---|---|
| 300 – 578 | Bajo |
| 579 – 668 | Medio |
| 669 – 738 | Bueno |
| 739 – 849 | Excelente |

La variable generada es:

```text
nivel_credito
```

Esta clasificación se utiliza exclusivamente para análisis y segmentación del
dataset.

**No representa una decisión crediticia real ni un modelo de evaluación de
riesgo financiero.**

---

## Estado de pago

Los estados originales son transformados para facilitar su interpretación:

| Estado original | Estado transformado |
|---|---|
| Paid On Time | Al Día |
| Late Payment | Pago Tardío |
| Defaulted | Incumplimiento |

La variable generada es:

```text
estado_pago
```

---

# 🗄️ 4. Almacenamiento

Los datos procesados son almacenados en:

```text
bnpl_analytics.db
```

utilizando **SQLite**.

La tabla principal es:

```text
clientes_credito
```

La base de datos se genera automáticamente durante la ejecución del pipeline.

La tabla procesada se reconstruye a partir del dataset de entrada en cada
ejecución.

---

# 📊 Capa analítica SQL

El proyecto genera tres vistas SQL orientadas al análisis del comportamiento
de las operaciones BNPL.

---

## `v_riesgo_por_edad`

Permite analizar las operaciones según el segmento de edad.

Incluye:

- Segmento de edad.
- Cantidad de operaciones.
- Cantidad de incumplimientos.
- Tasa de incumplimiento.
- Monto promedio de compra.

La tasa se calcula a partir de:

```text
incumplimientos / total de operaciones × 100
```

---

## `v_riesgo_por_proveedor`

Permite analizar las operaciones según el proveedor BNPL.

Incluye:

- Proveedor.
- Cantidad de operaciones.
- Cantidad de incumplimientos.
- Tasa de incumplimiento.
- Monto total de compras.

---

## `v_riesgo_por_categoria`

Permite analizar las operaciones según la categoría de compra.

Incluye:

- Categoría.
- Cantidad de operaciones.
- Cantidad de incumplimientos.
- Tasa de incumplimiento.
- Monto promedio de compra.
- Monto total de compras.

---

# 📈 Resultado de una ejecución

En la ejecución utilizada para documentar el proyecto se obtuvieron:

```text
Registros extraídos:       50,000
Registros eliminados:           0
Registros procesados:       50,000
```

Los controles de calidad implementados no detectaron registros inválidos en
esta ejecución.

### Controles realizados

```text
Credit Score fuera de rango:       0
Edad fuera de rango:               0
Ingresos inválidos:                0
Purchase Amount inválido:          0
Estado de pago inesperado:         0
Duplicados:                        0
Valores nulos:                     0
```

Estos resultados corresponden a una ejecución concreta del dataset utilizado
en el proyecto.

---

# 📊 Análisis por rango de edad

Resultado obtenido:

| Segmento | Operaciones | Incumplimientos | Tasa | Compra promedio |
|---|---:|---:|---:|---:|
| Joven | 8,421 | 854 | 10.14% | 557.37 |
| Senior | 4,290 | 383 | 8.93% | 568.36 |
| Adulto | 21,143 | 1,801 | 8.52% | 560.77 |
| Adulto Joven | 16,146 | 1,341 | 8.31% | 568.12 |

Las métricas son descriptivas y corresponden al dataset procesado por el
pipeline.

---

# 🏦 Análisis por proveedor BNPL

Resultado obtenido:

| Proveedor | Operaciones | Incumplimientos | Tasa | Monto total |
|---|---:|---:|---:|---:|
| Sezzle | 12,501 | 1,114 | 8.91% | 7,048,220 |
| Afterpay | 12,536 | 1,114 | 8.89% | 7,082,894 |
| Affirm | 12,418 | 1,073 | 8.64% | 6,923,641 |
| Klarna | 12,545 | 1,078 | 8.59% | 7,106,344 |

Estas métricas permiten analizar la distribución de las operaciones y los
incumplimientos según proveedor.

---

# 🛍️ Análisis por categoría

Resultado obtenido:

| Categoría | Operaciones | Incumplimientos | Tasa | Compra promedio | Monto total |
|---|---:|---:|---:|---:|---:|
| Electronics | 8,303 | 794 | 9.56% | 1,102.67 | 9,155,487 |
| Travel | 8,401 | 795 | 9.46% | 1,630.55 | 13,698,230 |
| Fashion | 8,307 | 729 | 8.78% | 159.88 | 1,328,141 |
| Beauty | 8,381 | 710 | 8.47% | 158.87 | 1,331,483 |
| Groceries | 8,240 | 697 | 8.46% | 159.31 | 1,312,731 |
| Home & Furniture | 8,368 | 654 | 7.82% | 159.54 | 1,335,027 |

Estas métricas corresponden a una ejecución concreta del dataset.

---

# 📝 Logging

El pipeline registra información durante las diferentes etapas del proceso.

El logging permite visualizar:

- Inicio de la ejecución.
- Cantidad de registros extraídos.
- Resultados de los controles de calidad.
- Registros eliminados.
- Cantidad de registros procesados.
- Creación de la base de datos.
- Creación de las vistas SQL.
- Resultados de las consultas analíticas.
- Errores durante la ejecución.

El archivo generado es:

```text
registro_bnpl.log
```

---

# 🐳 Docker

El proyecto incluye:

```text
Dockerfile
docker-compose.yml
```

El `Dockerfile` utiliza Python 3.11 y permite instalar las dependencias
definidas en `requirements.txt`.

Desde el directorio del proyecto:

```cmd
docker compose up --build
```

---

# 🐍 Ejecución local

## Requisitos

- Python 3.11 o compatible.
- Pip.

### 1. Crear entorno virtual

```cmd
python -m venv .venv
```

### 2. Activar entorno virtual

En Windows:

```cmd
.venv\Scripts\activate
```

### 3. Instalar dependencias

```cmd
pip install -r requirements.txt
```

### 4. Ejecutar el pipeline

```cmd
python bnpl_pipeline.py
```

Al finalizar se generará:

```text
bnpl_analytics.db
registro_bnpl.log
```

---

# 🧰 Tecnologías

- Python 3.11
- Pandas
- SQLite
- SQL
- Docker
- Docker Compose
- Logging
- Git

---

# 📚 Conceptos demostrados

Este proyecto demuestra conocimientos prácticos en:

```text
ETL
│
├── Extract
├── Transform
└── Load

Data Engineering
│
├── Data Quality
├── Data Validation
├── Feature Engineering
└── Logging

Data Analytics
│
├── SQL
├── Aggregations
├── Analytical Views
├── Segmentation
└── Business Metrics

Data Storage
│
└── SQLite
```

---

# ⚠️ Limitaciones

Este proyecto está diseñado como una implementación educativa y de portafolio.

Actualmente:

- El origen de datos es un archivo CSV.
- El almacenamiento utiliza SQLite.
- El pipeline se ejecuta manualmente.
- No existe procesamiento incremental.
- No existe orquestación externa.
- Las segmentaciones son reglas definidas dentro del pipeline.
- Las métricas generadas son descriptivas.
- No se utiliza Machine Learning para realizar predicciones.
- La clasificación de `Credit_Score` no representa una decisión crediticia real.

---

# 🚀 Próximas mejoras

Como evolución futura del proyecto podrían incorporarse:

- Tests automatizados.
- Procesamiento incremental.
- Orquestación mediante Airflow o Prefect.
- Almacenamiento en PostgreSQL.
- Uso de Parquet.
- Mayor cantidad de métricas analíticas.
- Dashboards para visualización.
- Validaciones automatizadas más extensas.
- Data lineage.
- Monitoreo y observabilidad del pipeline.

---

# 🎯 Objetivo dentro del portafolio

Este proyecto corresponde al **segundo nivel del portfolio de Data Engineering**.

La finalidad es demostrar una evolución respecto al pipeline anterior,
incorporando:

```text
ETL
 ↓
Data Quality
 ↓
Feature Engineering
 ↓
Segmentación
 ↓
SQLite
 ↓
SQL Analytics
```

El proyecto muestra cómo un pipeline puede transformar datos operacionales
en información estructurada para análisis.

---

# 💼 Competencias demostradas

Este proyecto demuestra experiencia práctica en:

- Construcción de pipelines ETL con Python.
- Procesamiento de datos con Pandas.
- Validación y limpieza de datasets.
- Implementación de controles de Data Quality.
- Conversión y validación de tipos de datos.
- Validación de rangos y reglas de negocio.
- Feature Engineering.
- Segmentación de datos.
- Transformación de variables categóricas.
- Persistencia de datos utilizando SQLite.
- Creación de tablas y vistas SQL.
- Uso de funciones de agregación.
- Generación de métricas descriptivas.
- Análisis por edad, proveedor y categoría.
- Logging de procesos ETL.
- Manejo de errores.
- Ejecución mediante Docker.
- Organización de un proyecto orientado a Data Engineering y Data Analytics.