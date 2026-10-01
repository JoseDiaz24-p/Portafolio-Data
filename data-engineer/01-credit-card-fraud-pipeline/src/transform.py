import pandas as pd

from src.extract import get_logger


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_logger()

    logger.info(
        "[2/3] Limpiando y transformando datos..."
    )

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
            f"Faltan columnas requeridas: "
            f"{columnas_faltantes}"
        )

    registros_iniciales = len(df)

    # Conversión de tipos
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df["is_fraud"] = pd.to_numeric(
        df["is_fraud"],
        errors="coerce"
    )

    # Data Quality
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

    # Limpieza
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

    # Feature Engineering
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

    df["tipo_transaccion"] = df["is_fraud"].map(
        {
            0: "Legítima",
            1: "Fraude"
        }
    )

    registros_finales = len(df)

    registros_eliminados = (
        registros_iniciales - registros_finales
    )

    logger.info(
        f"-> Registros eliminados durante "
        f"la limpieza: {registros_eliminados:,}"
    )

    logger.info(
        f"-> Registros procesados: "
        f"{registros_finales:,}"
    )

    return df