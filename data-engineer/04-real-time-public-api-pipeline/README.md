# Real-Time Public API Data Pipeline & Analytics

Pipeline de datos desarrollado en Python para extraer información meteorológica desde una API pública, procesarla y almacenarla en Supabase (PostgreSQL).

El proyecto busca simular un flujo de trabajo de Data Engineering utilizando extracción de datos, transformación, almacenamiento RAW/CLEAN y carga incremental.

## Arquitectura


Open-Meteo API
       │
       ▼
   Python
   requests
       │
       ▼
  Datos RAW
       │
       ▼
     pandas
       │
       ▼
 Transformación
 y limpieza
       │
       ▼
 Datos CLEAN
       │
       ▼
Supabase / PostgreSQL
       │
       ▼
    Power BI