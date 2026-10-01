import pandas as pd

from src.extract import get_logger


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


def validar_columnas(df: pd.DataFrame) -> None:
    columnas_faltantes = [
        columna
        for columna in REQUIRED_COLUMNS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(columnas_faltantes)
        )


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_logger()

    logger.info(
        "[2/3] Validando, limpiando y transformando datos BNPL..."
    )

    validar_columnas(df)

    df = df.copy()

    registros_iniciales = len(df)

    # --------------------------------------------------------
    # Conversión de tipos numéricos
    # --------------------------------------------------------

    columnas_numericas = [
        "Customer_Age",
        "Annual_Income",
        "Credit_Score",
        "Purchase_Amount",
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Data Quality
    # --------------------------------------------------------

    duplicados = df["Transaction_ID"].duplicated().sum()

    nulos = (
        df[REQUIRED_COLUMNS]
        .isnull()
        .any(axis=1)
        .sum()
    )

    edades_invalidas = (
        (df["Customer_Age"] < 18)
        | (df["Customer_Age"] > 64)
    ).sum()

    ingresos_invalidos = (
        df["Annual_Income"] <= 0
    ).sum()

    compras_invalidas = (
        df["Purchase_Amount"] <= 0
    ).sum()

    credit_score_invalido = (
        (df["Credit_Score"] < 300)
        | (df["Credit_Score"] > 849)
    ).sum()

    estados_invalidos = (
        ~df["Repayment_Status"]
        .isin(VALID_REPAYMENT_STATUS)
    ).sum()

    logger.info(
        f"-> Duplicados detectados: {duplicados:,}"
    )

    logger.info(
        f"-> Registros con valores nulos: {nulos:,}"
    )

    logger.info(
        f"-> Edades inválidas: {edades_invalidas:,}"
    )

    logger.info(
        f"-> Ingresos inválidos: {ingresos_invalidos:,}"
    )

    logger.info(
        f"-> Montos de compra inválidos: {compras_invalidas:,}"
    )

    logger.info(
        f"-> Credit Score inválidos: "
        f"{credit_score_invalido:,}"
    )

    logger.info(
        f"-> Estados de pago inválidos: "
        f"{estados_invalidos:,}"
    )

    # --------------------------------------------------------
    # Limpieza
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["Transaction_ID"],
        keep="first"
    )

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    )

    df = df[
        (df["Customer_Age"] >= 18)
        & (df["Customer_Age"] <= 64)
        & (df["Annual_Income"] > 0)
        & (df["Purchase_Amount"] > 0)
        & (df["Credit_Score"] >= 300)
        & (df["Credit_Score"] <= 849)
        & (
            df["Repayment_Status"]
            .isin(VALID_REPAYMENT_STATUS)
        )
        & (
            df["Transaction_ID"]
            .astype(str)
            .str.strip()
            != ""
        )
    ].copy()

    # --------------------------------------------------------
    # Feature Engineering: rango de edad
    # --------------------------------------------------------

    bins_edad = [
        18,
        26,
        41,
        61,
        float("inf")
    ]

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

    # --------------------------------------------------------
    # Feature Engineering: nivel de crédito
    # --------------------------------------------------------

    bins_credito = [
        299,
        579,
        669,
        739,
        849
    ]

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

    # --------------------------------------------------------
    # Normalización semántica del estado de pago
    # --------------------------------------------------------

    df["estado_pago"] = df["Repayment_Status"].map(
        {
            "Paid On Time": "Al Día",
            "Late Payment": "Pago Tardío",
            "Defaulted": "Incumplimiento"
        }
    )

    registros_eliminados = (
        registros_iniciales - len(df)
    )

    logger.info(
        "-> Registros eliminados durante la limpieza: "
        f"{registros_eliminados:,}"
    )

    logger.info(
        f"-> Registros procesados: {len(df):,}"
    )

    return df