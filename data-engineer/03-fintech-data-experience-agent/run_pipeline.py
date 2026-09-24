import os
import logging
import sqlite3
import pandas as pd

from src.etl.transformador import FintechTransformadorDatos


def run_etl():
    directorio_base = os.path.dirname(os.path.abspath(__file__))

    ruta_dataset = os.path.join(
        directorio_base,
        "data",
        "digital_wallet_ltv_dataset.csv"
    )

    ruta_database = os.path.join(
        directorio_base,
        "database",
        "mach_analytics.db"
    )

    ruta_log = os.path.join(
        directorio_base,
        "registro_logs.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(ruta_log, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("run_pipeline")

    logger.info(f"[1/3] Extrayendo datos desde: {ruta_dataset}")

    if not os.path.exists(ruta_dataset):
        logger.error(f"No se encontró el dataset en: {ruta_dataset}")
        raise FileNotFoundError(
            f"Archivo no disponible: {ruta_dataset}"
        )

    df_inicial = pd.read_csv(ruta_dataset)

    logger.info(
        f"-> Registros extraídos: {len(df_inicial):,}"
    )

    logger.info(
        "[2/3] Ejecutando limpieza y transformación de datos..."
    )

    transformador = FintechTransformadorDatos(df_inicial)

    df_procesado = (
        transformador
        .limpieza_datos()
        .agregar_metricas_negocio()
        .datos_limpios()
    )

    logger.info(
        f"-> Registros procesados: {len(df_procesado):,}"
    )

    os.makedirs(
        os.path.dirname(ruta_database),
        exist_ok=True
    )

    logger.info(
        f"[3/3] Cargando datos en: {ruta_database}"
    )

    conn = sqlite3.connect(ruta_database)

    try:
        df_procesado.to_sql(
            "dim_customers_ltv",
            conn,
            if_exists="replace",
            index=False
        )

        cursor = conn.cursor()

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_id
            ON dim_customers_ltv (Customer_ID);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_segment
            ON dim_customers_ltv (Customer_Segment);
        """)

        conn.commit()

    finally:
        conn.close()

    logger.info(
        "Pipeline ETL finalizado correctamente."
    )


if __name__ == "__main__":
    run_etl()