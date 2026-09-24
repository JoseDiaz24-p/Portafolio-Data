import os
import logging
import sqlite3
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_RAW = os.path.join(
    BASE_DIR,
    "data",
    "credit_card.csv"
)

DB_OUTPUT = os.path.join(
    BASE_DIR,
    "fraud_warehouse.db"
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "registro_fraudes.log"
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("etl_pipeline")


# ============================================================
# EXTRACT
# ============================================================

def extract_data(ruta: str) -> pd.DataFrame:
    logger.info(f"[1/3] Extrayendo datos desde: {ruta}")

    if not os.path.exists(ruta):
        logger.error(f"No se encontró el dataset en: {ruta}")
        raise FileNotFoundError(
            f"Archivo no disponible: {ruta}"
        )

    df = pd.read_csv(ruta)

    logger.info(
        f"-> Registros extraídos: {len(df):,}"
    )

    return df


# ============================================================
# DATA QUALITY + TRANSFORM
# ============================================================

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("[2/3] Limpiando y transformando datos...")

    columnas_requeridas = [
        "transaction_id",
        "amount",
        "is_fraud",
        "merchant_category"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas requeridas: {columnas_faltantes}"
        )

    registros_iniciales = len(df)

    # --------------------------------------------------------
    # Conversión de tipos
    # --------------------------------------------------------

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df["is_fraud"] = pd.to_numeric(
        df["is_fraud"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Data Quality
    # --------------------------------------------------------

    duplicados = df.duplicated(
        subset=["transaction_id"]
    ).sum()

    nulos_antes = df.isnull().any(axis=1).sum()

    valores_fraude_invalidos = (
        ~df["is_fraud"].isin([0, 1])
    ).sum()

    montos_invalidos = (
        df["amount"] <= 0
    ).sum()

    logger.info(
        f"-> Duplicados detectados: {duplicados:,}"
    )

    logger.info(
        f"-> Registros con valores nulos: {nulos_antes:,}"
    )

    logger.info(
        f"-> Valores is_fraud inválidos: "
        f"{valores_fraude_invalidos:,}"
    )

    logger.info(
        f"-> Montos inválidos: {montos_invalidos:,}"
    )

    # --------------------------------------------------------
    # Limpieza
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["transaction_id"],
        keep="first"
    )

    df = df.dropna(
        subset=columnas_requeridas
    )

    df = df[
        df["transaction_id"]
        .astype(str)
        .str.strip()
        != ""
    ]

    df = df[
        df["is_fraud"].isin([0, 1])
    ]

    df = df[
        df["amount"] > 0
    ]

    # --------------------------------------------------------
    # Feature Engineering
    # --------------------------------------------------------

    bins = [
        0,
        50,
        200,
        1000,
        float("inf")
    ]

    labels = [
        "Bajo (0-50)",
        "Medio (50-200)",
        "Alto (200-1000)",
        "Crítico (>1000)"
    ]

    df["rango_monto"] = pd.cut(
        df["amount"],
        bins=bins,
        labels=labels,
        right=False
    )

    df["tipo_transaccion"] = df[
        "is_fraud"
    ].apply(
        lambda x: "Fraude"
        if x == 1
        else "Legítima"
    )

    registros_finales = len(df)
    registros_eliminados = (
        registros_iniciales - registros_finales
    )

    logger.info(
        f"-> Registros eliminados durante la limpieza: "
        f"{registros_eliminados:,}"
    )

    logger.info(
        f"-> Registros procesados: "
        f"{registros_finales:,}"
    )

    return df


# ============================================================
# LOAD
# ============================================================

def load_data(
    df: pd.DataFrame,
    db_path: str
):
    logger.info(
        "[3/3] Cargando datos en SQLite..."
    )

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        # ----------------------------------------------------
        # Recrear tabla de forma determinista
        # ----------------------------------------------------

        cursor.execute(
            "DROP VIEW IF EXISTS v_resumen_categoria;"
        )

        cursor.execute(
            "DROP VIEW IF EXISTS v_resumen_riesgo;"
        )

        df.to_sql(
            "transacciones_bancarias",
            conn,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Vista: resumen por categoría
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_resumen_categoria AS
            SELECT
                merchant_category AS categoria_comercio,
                COUNT(transaction_id) AS total_operaciones,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS total_fraudes,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    / COUNT(transaction_id),
                    2
                ) AS tasa_fraude_porcentaje,

                ROUND(
                    AVG(amount),
                    2
                ) AS ticket_promedio,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN amount
                            ELSE 0
                        END
                    ),
                    2
                ) AS total_defraudado

            FROM transacciones_bancarias

            GROUP BY merchant_category;
        """)

        # ----------------------------------------------------
        # Vista: resumen por rango de monto
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_resumen_riesgo AS
            SELECT
                rango_monto,

                COUNT(transaction_id)
                    AS total_transacciones,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS casos_fraude,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    / COUNT(transaction_id),
                    2
                ) AS tasa_fraude_porcentaje,

                ROUND(
                    AVG(amount),
                    2
                ) AS monto_promedio,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN amount
                            ELSE 0
                        END
                    ),
                    2
                ) AS monto_total_defraudado

            FROM transacciones_bancarias

            GROUP BY rango_monto;
        """)

        conn.commit()

        logger.info(
            "-> Tabla y vistas analíticas creadas correctamente."
        )

        # ----------------------------------------------------
        # Reporte por categoría
        # ----------------------------------------------------

        reporte_categoria = cursor.execute(
            """
            SELECT *
            FROM v_resumen_categoria
            ORDER BY tasa_fraude_porcentaje DESC;
            """
        ).fetchall()

        logger.info(
            "\n--- REPORTE DE FRAUDE POR CATEGORÍA ---"
        )

        for fila in reporte_categoria:
            logger.info(
                f"Categoría: {fila[0]:<15} | "
                f"Operaciones: {fila[1]:<5} | "
                f"Fraudes: {fila[2]:<4} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Defraudado: ${fila[5]:,.2f}"
            )

        # ----------------------------------------------------
        # Reporte por rango de monto
        # ----------------------------------------------------

        reporte_riesgo = cursor.execute(
            """
            SELECT *
            FROM v_resumen_riesgo
            ORDER BY tasa_fraude_porcentaje DESC;
            """
        ).fetchall()

        logger.info(
            "\n--- REPORTE DE FRAUDE POR RANGO DE MONTO ---"
        )

        for fila in reporte_riesgo:
            logger.info(
                f"Rango: {fila[0]:<18} | "
                f"Transacciones: {fila[1]:<5} | "
                f"Fraudes: {fila[2]:<4} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Defraudado: ${fila[5]:,.2f}"
            )

    finally:
        conn.close()


# ============================================================
# PIPELINE
# ============================================================

def run_pipeline():
    try:
        raw_df = extract_data(DATA_RAW)

        clean_df = transform_data(raw_df)

        load_data(
            clean_df,
            DB_OUTPUT
        )

        logger.info(
            "\nPipeline de fraude ejecutado exitosamente."
        )

    except Exception as error:
        logger.critical(
            f"\nError en el pipeline: {error}"
        )
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()