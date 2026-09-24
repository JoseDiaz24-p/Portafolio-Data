import os
import logging
import sqlite3
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "data", "bnpl.csv")
DB_OUTPUT = os.path.join(BASE_DIR, "bnpl_analytics.db")
LOG_FILE = os.path.join(BASE_DIR, "registro_bnpl.log")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("bnpl_pipeline")


REQUIRED_COLUMNS = [
    "Transaction_ID",
    "Customer_Age",
    "Gender",
    "Annual_Income",
    "Credit_Score",
    "Purchase_Category",
    "BNPL_Provider",
    "Purchase_Amount",
    "Repayment_Status",
]

VALID_REPAYMENT_STATUS = {
    "Paid On Time",
    "Late Payment",
    "Defaulted",
}


def extraer_datos(ruta: str) -> pd.DataFrame:
    logger.info(f"[1/3] Extrayendo datos desde: {ruta}")

    if not os.path.exists(ruta):
        logger.error(f"No se encontró el dataset en {ruta}")
        raise FileNotFoundError(f"No se encontró el archivo en {ruta}")

    df = pd.read_csv(ruta)

    logger.info(f"-> Registros extraídos: {len(df):,}")

    return df


def validar_columnas(df: pd.DataFrame):
    columnas_faltantes = [
        columna
        for columna in REQUIRED_COLUMNS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}"
        )


def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("[2/3] Validando, limpiando y transformando datos BNPL...")

    validar_columnas(df)

    df = df.copy()

    registros_iniciales = len(df)

    # Conversión de tipos numéricos
    columnas_numericas = [
        "Customer_Age",
        "Annual_Income",
        "Credit_Score",
        "Purchase_Amount",
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # Data Quality
    duplicados = df["Transaction_ID"].duplicated().sum()
    nulos = df[REQUIRED_COLUMNS].isnull().any(axis=1).sum()

    edades_invalidas = (
        (df["Customer_Age"] < 18) |
        (df["Customer_Age"] > 64)
    ).sum()

    ingresos_invalidos = (
        df["Annual_Income"] <= 0
    ).sum()

    compras_invalidas = (
        df["Purchase_Amount"] <= 0
    ).sum()

    credit_score_invalido = (
        (df["Credit_Score"] < 300) |
        (df["Credit_Score"] > 849)
    ).sum()

    estados_invalidos = (
        ~df["Repayment_Status"].isin(VALID_REPAYMENT_STATUS)
    ).sum()

    logger.info(f"-> Duplicados detectados: {duplicados:,}")
    logger.info(f"-> Registros con valores nulos: {nulos:,}")
    logger.info(f"-> Edades inválidas: {edades_invalidas:,}")
    logger.info(f"-> Ingresos inválidos: {ingresos_invalidos:,}")
    logger.info(f"-> Montos de compra inválidos: {compras_invalidas:,}")
    logger.info(f"-> Credit Score inválidos: {credit_score_invalido:,}")
    logger.info(f"-> Estados de pago inválidos: {estados_invalidos:,}")

    # Limpieza
    df = df.drop_duplicates(
        subset=["Transaction_ID"],
        keep="first"
    )

    df = df.dropna(subset=REQUIRED_COLUMNS)

    df = df[
        (df["Customer_Age"] >= 18) &
        (df["Customer_Age"] <= 64) &
        (df["Annual_Income"] > 0) &
        (df["Purchase_Amount"] > 0) &
        (df["Credit_Score"] >= 300) &
        (df["Credit_Score"] <= 849) &
        (df["Repayment_Status"].isin(VALID_REPAYMENT_STATUS)) &
        (df["Transaction_ID"].astype(str).str.strip() != "")
    ].copy()

    # Feature Engineering: rango de edad
    bins_edad = [18, 26, 41, 61, float("inf")]
    labels_edad = [
        "Joven (18-25)",
        "Adulto Joven (26-40)",
        "Adulto (41-60)",
        "Senior (>60)"
    ]

    df["rango_edad"] = pd.cut(
        df["Customer_Age"],
        bins=bins_edad,
        labels=labels_edad,
        right=False
    )

    # Feature Engineering: nivel de crédito
    bins_credito = [299, 579, 669, 739, 849]
    labels_credito = [
        "Bajo",
        "Medio",
        "Bueno",
        "Excelente"
    ]

    df["nivel_credito"] = pd.cut(
        df["Credit_Score"],
        bins=bins_credito,
        labels=labels_credito,
        right=True
    )

    # Normalización semántica del estado de pago
    df["estado_pago"] = df["Repayment_Status"].map({
        "Paid On Time": "Al Día",
        "Late Payment": "Pago Tardío",
        "Defaulted": "Incumplimiento"
    })

    registros_eliminados = registros_iniciales - len(df)

    logger.info(
        f"-> Registros eliminados durante la limpieza: "
        f"{registros_eliminados:,}"
    )

    logger.info(f"-> Registros procesados: {len(df):,}")

    return df


def cargar_datos(df: pd.DataFrame, db_path: str):
    logger.info("[3/3] Cargando datos en SQLite...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("DROP VIEW IF EXISTS v_riesgo_por_edad")
        cursor.execute("DROP VIEW IF EXISTS v_riesgo_por_proveedor")
        cursor.execute("DROP VIEW IF EXISTS v_riesgo_por_categoria")

        df.to_sql(
            "clientes_credito",
            conn,
            if_exists="replace",
            index=False
        )

        # Vista 1: riesgo por rango de edad
        cursor.execute("""
        CREATE VIEW v_riesgo_por_edad AS
        SELECT
            rango_edad,
            COUNT(Transaction_ID) AS total_clientes,
            SUM(
                CASE
                    WHEN Repayment_Status = 'Defaulted'
                    THEN 1 ELSE 0
                END
            ) AS total_incumplimientos,
            ROUND(
                AVG(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1.0 ELSE 0.0
                    END
                ) * 100,
                2
            ) AS tasa_incumplimiento_porcentaje,
            ROUND(AVG(Purchase_Amount), 2) AS compra_promedio
        FROM clientes_credito
        GROUP BY rango_edad;
        """)

        # Vista 2: riesgo por proveedor BNPL
        cursor.execute("""
        CREATE VIEW v_riesgo_por_proveedor AS
        SELECT
            BNPL_Provider AS proveedor_bnpl,
            COUNT(Transaction_ID) AS total_operaciones,
            SUM(
                CASE
                    WHEN Repayment_Status = 'Defaulted'
                    THEN 1 ELSE 0
                END
            ) AS total_incumplimientos,
            ROUND(
                AVG(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1.0 ELSE 0.0
                    END
                ) * 100,
                2
            ) AS tasa_incumplimiento_porcentaje,
            ROUND(SUM(Purchase_Amount), 2) AS monto_total_compras
        FROM clientes_credito
        GROUP BY BNPL_Provider;
        """)

        # Vista 3: riesgo por categoría
        cursor.execute("""
        CREATE VIEW v_riesgo_por_categoria AS
        SELECT
            Purchase_Category AS categoria_compra,
            COUNT(Transaction_ID) AS total_operaciones,
            SUM(
                CASE
                    WHEN Repayment_Status = 'Defaulted'
                    THEN 1 ELSE 0
                END
            ) AS total_incumplimientos,
            ROUND(
                AVG(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1.0 ELSE 0.0
                    END
                ) * 100,
                2
            ) AS tasa_incumplimiento_porcentaje,
            ROUND(AVG(Purchase_Amount), 2) AS compra_promedio,
            ROUND(SUM(Purchase_Amount), 2) AS monto_total_compras
        FROM clientes_credito
        GROUP BY Purchase_Category;
        """)

        conn.commit()

        logger.info(
            "-> Tabla 'clientes_credito' y vistas analíticas "
            "creadas correctamente."
        )

        logger.info("--- REPORTE DE INCUMPLIMIENTO POR EDAD ---")

        reporte_edad = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_edad
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_edad:
            logger.info(
                f"Grupo: {fila[0]:<22} | "
                f"Clientes: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Compra promedio: ${fila[4]:,.2f}"
            )

        logger.info("--- REPORTE DE INCUMPLIMIENTO POR PROVEEDOR ---")

        reporte_proveedor = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_proveedor
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_proveedor:
            logger.info(
                f"Proveedor: {fila[0]:<10} | "
                f"Operaciones: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Monto: ${fila[4]:,.2f}"
            )

        logger.info("--- REPORTE DE INCUMPLIMIENTO POR CATEGORÍA ---")

        reporte_categoria = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_categoria
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_categoria:
            logger.info(
                f"Categoría: {fila[0]:<18} | "
                f"Operaciones: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Compra promedio: ${fila[4]:,.2f} | "
                f"Monto total: ${fila[5]:,.2f}"
            )

    finally:
        conn.close()


def run_pipeline():
    try:
        raw_df = extraer_datos(DATA_RAW)
        clean_df = transformar_datos(raw_df)
        cargar_datos(clean_df, DB_OUTPUT)

        logger.info("Pipeline BNPL ejecutado exitosamente.")

    except Exception as e:
        logger.critical(f"Error en el proceso: {str(e)}")
        raise


if __name__ == "__main__":
    run_pipeline()