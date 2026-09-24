# 🤖 Fintech Data Experience & AI Agent

## Proyecto 03 — Data Engineering, Data Analytics & AI Integration

Proyecto orientado al procesamiento y análisis de datos de clientes de una
fintech, combinando un pipeline ETL en **Python y Pandas**, almacenamiento en
**SQLite**, consultas analíticas mediante **SQL** e integración experimental
con **Google Gemini** mediante Function Calling.

El proyecto demuestra una evolución desde el procesamiento tradicional de datos
hacia una arquitectura donde un agente puede consultar información almacenada
en una base de datos antes de generar una respuesta analítica.

El flujo principal es:

```text
CSV
 ↓
ETL
 ↓
Data Quality
 ↓
Feature Engineering
 ↓
SQLite
 ↓
SQL Analytics
 ↓
Gemini Function Calling
 ↓
Consulta de datos
 ↓
Análisis generado por IA
```

> La integración con IA es experimental y complementaria. El objetivo principal
> del proyecto es demostrar capacidades de Data Engineering, Data Analytics,
> procesamiento de datos e integración de herramientas externas.

---

# 🎯 Objetivo

Construir una solución capaz de:

- Extraer datos de clientes desde un archivo CSV.
- Validar y limpiar los datos.
- Generar métricas derivadas.
- Crear segmentos de clientes.
- Almacenar los datos procesados en SQLite.
- Crear consultas SQL para análisis.
- Exponer información de clientes mediante una herramienta parametrizada.
- Integrar un modelo de lenguaje mediante Function Calling.
- Permitir que el agente consulte información de un cliente antes de generar
  su análisis.
- Manejar errores y respuestas temporales del servicio externo.
- Ejecutar el pipeline mediante Python o Docker.

---

# 🏗️ Arquitectura

```text
                 ┌─────────────────────┐
                 │      CSV Dataset    │
                 │ digital_wallet_ltv  │
                 └──────────┬──────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │      ETL      │
                    │   Pandas      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Data Quality  │
                    │ Validaciones  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Transformación│
                    │ y métricas    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    SQLite     │
                    │ mach_analytics│
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
       ┌────────────────┐      ┌─────────────────┐
       │ SQL Analytics  │      │ Database Tool   │
       │ customer_kpis  │      │ get_customer_   │
       │                │      │ profile()       │
       └────────────────┘      └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Gemini Function │
                               │ Calling         │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ AI Customer     │
                               │ Analysis        │
                               └─────────────────┘
```

---

# 📂 Estructura del proyecto

```text
03-pipeline-fintech-data-experience-agent/
│
├── data/
│   └── digital_wallet_ltv_dataset.csv
│
├── database/
│   └── mach_analytics.db
│
├── src/
│   ├── ai_agent/
│   │   └── database_tool.py
│   │
│   ├── analytics/
│   │   └── customer_kpis.sql
│   │
│   └── etl/
│       └── transformador.py
│
├── .dockerignore
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run_agent.py
├── run_pipeline.py
└── README.md
```

### Archivos generados localmente

Durante la ejecución pueden generarse archivos como:

```text
mach_analytics.db
registro_logs.log
```

Estos archivos se mantienen fuera del control de versiones cuando corresponde.

La clave de API se configura mediante variables de entorno y no debe incluirse
directamente en el código fuente ni en el repositorio.

---

# 🔄 Pipeline ETL

## 1. Extract

El pipeline utiliza como fuente:

```text
data/digital_wallet_ltv_dataset.csv
```

El archivo contiene información relacionada con clientes y comportamiento
transaccional.

La extracción se realiza utilizando **Pandas**.

En la ejecución utilizada para documentar el proyecto se procesaron:

```text
7,000 registros
```

---

# 🧪 2. Data Quality

Antes de almacenar los datos se realizan validaciones para asegurar que la
información pueda ser procesada correctamente.

## Columnas requeridas

El pipeline verifica la existencia de:

```text
Customer_ID
Age
Location
Income_Level
Total_Transactions
Avg_Transaction_Value
Max_Transaction_Value
Min_Transaction_Value
Total_Spent
Active_Days
```

Si alguna columna requerida no existe, el procesamiento se detiene.

---

## Conversión de datos numéricos

Las columnas numéricas son convertidas a tipos apropiados antes de realizar
las transformaciones.

Entre ellas se encuentran:

```text
Age
Total_Transactions
Avg_Transaction_Value
Max_Transaction_Value
Min_Transaction_Value
Total_Spent
Active_Days
```

---

## Valores inválidos

El pipeline realiza controles sobre los datos antes de generar las métricas.

Entre las validaciones implementadas se encuentran:

- Conversión de columnas numéricas.
- Eliminación de registros con valores no procesables.
- Validación de `Active_Days > 0`.
- Validación de `Customer_ID` no vacío.
- Eliminación de clientes duplicados.

---

## Identificador del cliente

El campo:

```text
Customer_ID
```

se utiliza como identificador del cliente.

Los registros duplicados por `Customer_ID` son eliminados conservando una única
representación del cliente.

---

# 🧮 Feature Engineering

Después de la limpieza se generan métricas adicionales para facilitar el
análisis del comportamiento de los clientes.

---

## Daily Spend Rate

Se genera la métrica:

```text
Daily_Spend_Rate
```

que relaciona el gasto total con los días activos del cliente.

Esta métrica permite contextualizar el gasto respecto del período de actividad
registrado.

---

## Ticket Spread

También se genera:

```text
Ticket_Spread
```

relacionado con la diferencia entre el valor máximo y mínimo de las
transacciones registradas.

Esta variable permite observar la dispersión del valor de las operaciones del
cliente.

---

# 👥 Segmentación de clientes

El pipeline genera segmentos utilizando métricas derivadas del dataset.

Para la segmentación se utilizan percentiles calculados sobre:

```text
Total_Spent
Active_Days
```

En particular, se utiliza el percentil 75 (`P75`) como parte de las reglas de
segmentación.

Los segmentos generados son:

```text
VIP_ALTO_CONSUMO
COMPRADOR_DE_BAJA_FRECUENCIA
USUARIO_REGULAR
USUARIO_ESTANDAR
```

Estas categorías son utilizadas para análisis descriptivo del comportamiento
de los clientes.

No representan una clasificación comercial o financiera real.

---

# 🗄️ Almacenamiento

Los datos procesados se almacenan en:

```text
database/mach_analytics.db
```

utilizando **SQLite**.

La tabla principal es:

```text
dim_customers_ltv
```

La base de datos es creada automáticamente durante la ejecución del pipeline.

El proceso utiliza `replace` para reconstruir la tabla procesada a partir del
dataset de entrada.

---

# 📊 SQL Analytics

El proyecto incluye una capa independiente de análisis mediante SQL:

```text
src/analytics/customer_kpis.sql
```

Esta consulta trabaja sobre la tabla:

```text
dim_customers_ltv
```

y permite obtener información analítica de los clientes.

---

## Funciones analíticas utilizadas

El archivo SQL incorpora:

- `AVG() OVER(PARTITION BY Location)`
- `DENSE_RANK()`
- `LIMIT`

Estas funciones permiten generar métricas y rankings considerando el contexto
de cada ubicación.

El archivo SQL funciona como una capa de análisis independiente del proceso
principal de carga ETL.

---

# 🤖 Integración con Google Gemini

Una de las características principales del proyecto es la integración
experimental con un modelo de lenguaje mediante **Function Calling**.

El agente se encuentra implementado principalmente en:

```text
run_agent.py
```

y utiliza una herramienta definida en:

```text
src/ai_agent/database_tool.py
```

---

# 🔧 Database Tool

El proyecto implementa la función:

```text
get_customer_profile(customer_id)
```

Esta herramienta permite consultar información de un cliente específico
almacenada en SQLite.

El flujo es:

```text
Customer ID
     ↓
get_customer_profile()
     ↓
SQLite
     ↓
dim_customers_ltv
     ↓
Customer Profile
```

La consulta utiliza parámetros para evitar construir directamente la sentencia
SQL a partir del identificador recibido.

---

# 🔗 Function Calling

El agente declara una herramienta que permite consultar el perfil de un
cliente.

El modelo puede solicitar:

```text
get_customer_profile
```

proporcionando:

```text
customer_id
```

El programa recibe la solicitud de la herramienta, consulta SQLite y devuelve
la información obtenida al modelo.

El flujo completo es:

```text
Usuario
   │
   ▼
Pregunta sobre cliente
   │
   ▼
Gemini
   │
   ▼
Function Call
   │
   ▼
get_customer_profile()
   │
   ▼
SQLite
   │
   ▼
Perfil del cliente
   │
   ▼
Gemini
   │
   ▼
Respuesta analítica
```

Este enfoque permite separar la generación del lenguaje de la consulta de
datos.

---

# 🧠 Instrucciones del agente

El agente está configurado para trabajar como un agente de experiencia de
cliente para una fintech.

Entre las instrucciones implementadas se encuentran:

- Utilizar la herramienta para consultar información del cliente.
- No inventar datos.
- Analizar la información disponible.
- Entregar respuestas estructuradas.
- Evitar decisiones financieras automatizadas.
- Utilizar recomendaciones únicamente como apoyo al análisis.

El objetivo es que el modelo utilice datos obtenidos desde la fuente antes de
generar su respuesta.

---

# 🔐 Configuración de API

La API se configura mediante variables de entorno.

El proyecto incluye:

```text
.env
.env.example
```

El archivo `.env.example` contiene la estructura esperada:

```text
GEMINI_API_KEY=tu_api_key_aqui
```

La clave real debe mantenerse únicamente en el entorno local y nunca debe
subirse al repositorio.

---

# 🛡️ Manejo de errores

El agente incorpora mecanismos para manejar errores relacionados con la
comunicación con el servicio externo.

Se contemplan respuestas temporales como:

```text
HTTP 429
HTTP 503
```

Cuando corresponde, el programa realiza reintentos utilizando una estrategia
de espera progresiva.

También se manejan:

- Timeouts.
- Errores de conexión.
- Respuestas inválidas.
- Ausencia de contenido.
- Errores relacionados con la herramienta.
- Errores de SQLite.

Si el servicio de Gemini no está disponible después de los reintentos, el
programa termina de forma controlada e informa que el agente no está
disponible temporalmente.

---

# 📈 Resultado de una ejecución

En una ejecución del pipeline ETL se obtuvieron:

```text
Registros extraídos:       7,000
Registros eliminados:           0
Registros procesados:       7,000
```

La base de datos utilizada fue:

```text
database/mach_analytics.db
```

El pipeline completó correctamente la etapa de procesamiento y almacenamiento.

---

# 🤖 Resultado del agente

La disponibilidad del agente depende del servicio externo de Gemini.

Durante una ejecución de prueba, el servicio respondió temporalmente con:

```text
HTTP 429
```

El programa manejó esta situación mediante el mecanismo de reintentos
implementado y terminó de forma controlada:

```text
AGENTE NO DISPONIBLE
Gemini no está disponible temporalmente (HTTP 429).
```

Esto demuestra que el flujo contempla escenarios en los que el servicio
externo no se encuentra disponible.

---

# 📝 Logging

El proyecto registra información durante la ejecución del pipeline.

El archivo utilizado es:

```text
registro_logs.log
```

El logging permite realizar seguimiento de:

- Inicio del pipeline.
- Cantidad de registros extraídos.
- Transformaciones.
- Registros procesados.
- Creación de la base de datos.
- Errores durante el procesamiento.
- Ejecución del agente.
- Errores de comunicación con Gemini.

---

# 🐳 Docker

El proyecto incluye:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

El contenedor utiliza:

```text
Python 3.11
```

Las dependencias se instalan desde:

```text
requirements.txt
```

La ejecución del contenedor permite ejecutar el pipeline y posteriormente
iniciar el agente.

Desde el directorio del proyecto:

```cmd
docker compose up --build
```

---

# 🐍 Ejecución local

## Requisitos

- Python 3.11 o compatible.
- Pip.
- Una clave de API de Gemini configurada mediante `.env` para utilizar el
  agente.

---

## 1. Crear entorno virtual

```cmd
python -m venv .venv
```

---

## 2. Activar entorno virtual

En Windows:

```cmd
.venv\Scripts\activate
```

---

## 3. Instalar dependencias

```cmd
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

Crear un archivo:

```text
.env
```

basado en:

```text
.env.example
```

Agregar la clave de API correspondiente:

```text
GEMINI_API_KEY=tu_api_key
```

No subir este archivo al repositorio.

---

## 5. Ejecutar el pipeline

```cmd
python run_pipeline.py
```

Esto procesa el dataset y genera la base de datos:

```text
database/mach_analytics.db
```

---

## 6. Ejecutar el agente

Una vez disponible la base de datos:

```cmd
python run_agent.py
```

El agente realiza una consulta utilizando el cliente de prueba definido en el
programa y puede utilizar `get_customer_profile()` para recuperar la
información correspondiente desde SQLite.

---

# 🧰 Tecnologías

### Data Engineering

- Python 3.11
- Pandas
- ETL
- Data Quality
- Feature Engineering

### Data Analytics

- SQL
- SQLite
- SQL Window Functions
- Aggregations
- Customer Segmentation
- Business Metrics

### AI Integration

- Google Gemini API
- Function Calling
- Tool Calling
- Integración de LLM con fuentes de datos

### DevOps

- Docker
- Docker Compose
- Variables de entorno
- Logging

### Control de versiones

- Git
- GitHub

---

# 📚 Conceptos demostrados

Este proyecto integra diferentes áreas:

```text
DATA ENGINEERING
│
├── ETL
├── Data Quality
├── Feature Engineering
├── Data Transformation
└── SQLite

DATA ANALYTICS
│
├── SQL
├── Window Functions
├── Aggregations
├── Customer KPIs
└── Segmentation

AI INTEGRATION
│
├── Gemini API
├── Function Calling
├── Database Tools
├── Parameterized Queries
└── Error Handling

DEVOPS
│
├── Docker
├── Docker Compose
├── Environment Variables
└── Logging
```

---

# ⚠️ Limitaciones

Este proyecto está diseñado como una implementación educativa y de portafolio.

Actualmente:

- El origen de datos es un archivo CSV.
- El almacenamiento utiliza SQLite.
- El pipeline ETL se ejecuta manualmente.
- No existe procesamiento incremental.
- No existe una herramienta de orquestación externa.
- El análisis SQL se ejecuta de forma independiente.
- La integración con Gemini depende de la disponibilidad del servicio externo.
- No se implementa un sistema de Machine Learning para realizar predicciones.
- El agente no realiza decisiones financieras.
- La segmentación de clientes corresponde a reglas analíticas definidas dentro
  del proyecto.

---

# 🚀 Próximas mejoras

Como evolución futura del proyecto podrían incorporarse:

- Tests automatizados para ETL y herramientas.
- Procesamiento incremental.
- Orquestación mediante Airflow o Prefect.
- PostgreSQL como sistema de almacenamiento.
- Parquet como formato de datos.
- Data Warehouse.
- Mayor cantidad de KPIs.
- Dashboards para visualización.
- Observabilidad del pipeline.
- Métricas de calidad automatizadas.
- Evaluación sistemática de las respuestas del agente.
- Mayor cantidad de herramientas disponibles para el agente.
- Integración con otras fuentes de datos.

---

# 🎯 Objetivo dentro del portafolio

Este proyecto corresponde al **tercer nivel del portfolio de Data Engineering**.

Su propósito es demostrar una evolución desde pipelines ETL tradicionales hacia
una solución que integra:

```text
Datos
 ↓
ETL
 ↓
Data Quality
 ↓
Feature Engineering
 ↓
Base de datos
 ↓
SQL Analytics
 ↓
Database Tool
 ↓
Function Calling
 ↓
AI Agent
```

El proyecto busca demostrar cómo las capacidades de Data Engineering pueden
servir como base para construir aplicaciones que integren datos estructurados
con modelos de lenguaje.

---

# 💼 Competencias demostradas

Este proyecto demuestra experiencia práctica en:

- Construcción de pipelines ETL con Python.
- Procesamiento de datos con Pandas.
- Implementación de controles de Data Quality.
- Transformación y limpieza de datasets.
- Feature Engineering.
- Generación de métricas derivadas.
- Segmentación de clientes.
- Persistencia de datos utilizando SQLite.
- Creación de tablas e índices.
- Consultas SQL analíticas.
- Uso de funciones de ventana.
- Uso de agregaciones.
- Diseño de herramientas de consulta sobre bases de datos.
- Consultas SQL parametrizadas.
- Integración de APIs externas.
- Function Calling.
- Integración de LLM con fuentes de datos.
- Manejo de errores y reintentos.
- Variables de entorno.
- Docker y Docker Compose.
- Logging.
- Organización modular de proyectos de datos.