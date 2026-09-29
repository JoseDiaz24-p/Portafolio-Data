import pandas as pd
import numpy as np


# ============================================================
# VALIDACIÓN Y TRANSFORMACIÓN INICIAL
# ============================================================

def validar_datos(df: pd.DataFrame):

    columnas_requeridas = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan Columnas Requeridas: "
            f"{columnas_faltantes}"
        )

    return columnas_requeridas


def limpiar_datos(
    df: pd.DataFrame,
    columnas_requeridas: list
) -> pd.DataFrame:

    df = df.copy()
    df["InvoiceNo"] = (
        df["InvoiceNo"]
        .astype("string")
        .str.strip()
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    columnas_numericas = [
        "Quantity",
        "UnitPrice"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    return df


def enriquecer_datos(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    condicion = (
        df["InvoiceNo"]
        .astype(str)
        .str.startswith("C")
    )

    df["InvoiceNo_Tipo"] = np.where(
        condicion,
        "Cancelacion",
        "Venta Normal"
    )

    return df


def transformar_datos(
    df: pd.DataFrame
) -> pd.DataFrame:

    columnas_requeridas = validar_datos(df)

    df_limpio = limpiar_datos(
        df,
        columnas_requeridas
    )

    df_transformado = enriquecer_datos(
        df_limpio
    )

    return df_transformado


# ============================================================
# ANÁLISIS DE CALIDAD DE DATOS
# ============================================================

def analizar_calidad_datos(
    df: pd.DataFrame
):

    print("\n=== ANÁLISIS DE CALIDAD ===")

    print(
        f"Duplicados exactos: "
        f"{df.duplicated().sum():,}"
    )

    print(
        f"CustomerID nulos: "
        f"{df['CustomerID'].isna().sum():,}"
    )

    print(
        f"Description nulas: "
        f"{df['Description'].isna().sum():,}"
    )

    print(
        f"Quantity negativos: "
        f"{(df['Quantity'] < 0).sum():,}"
    )

    print(
        f"UnitPrice igual a 0: "
        f"{(df['UnitPrice'] == 0).sum():,}"
    )

    print(
        f"UnitPrice negativos: "
        f"{(df['UnitPrice'] < 0).sum():,}"
    )

    print("\nQuantity negativa por tipo de invoice:")

    print(
        df.loc[
            df["Quantity"] < 0,
            "InvoiceNo_Tipo"
        ].value_counts()
    )

    print("\nQuantity Positiva por tipo de invoice:")

    print(
        df.loc[
            df["Quantity"] > 0,
            "InvoiceNo_Tipo"
        ].value_counts()
    )

    print(
        "\nVentas normales con Quantity negativa:"
    )

    print(
        df[
            (df["Quantity"] < 0)
            &
            (df["InvoiceNo_Tipo"] == "Venta Normal")
        ][
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "UnitPrice",
                "CustomerID"
            ]
        ].head(20)
    )

    print(
        "\nQuantity negativa + UnitPrice = 0:"
    )

    print(
        (
            (df["Quantity"] < 0)
            &
            (df["UnitPrice"] == 0)
        ).sum()
    )

    print(
        "\nQuantity negativa + UnitPrice = 0 "
        "+ CustomerID nulo:"
    )

    print(
        (
            (df["Quantity"] < 0)
            &
            (df["UnitPrice"] == 0)
            &
            (df["CustomerID"].isna())
        ).sum()
    )

    print(
        "\nQuantity negativa + UnitPrice = 0 "
        "+ Description nula:"
    )

    print(
        (
            (df["Quantity"] < 0)
            &
            (df["UnitPrice"] == 0)
            &
            (df["Description"].isna())
        ).sum()
    )

    print("\nUnitPrice = 0 y Quantity positiva:")

    print(
        df[
            (df["UnitPrice"] == 0)
            &
            (df["Quantity"] > 0)
        ][
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "UnitPrice",
                "CustomerID"
            ]
        ].head(20)
    )

    print(
        "\nUnitPrice = 0 + Quantity positiva "
        "+ CustomerID:"
    )

    print(
        df[
            (df["UnitPrice"] == 0)
            &
            (df["Quantity"] > 0)
            &
            (df["CustomerID"].notna())
        ].shape[0]
    )

    print("\nDuplicados por tipo de Invoice:")

    print(
        df[
            df.duplicated(keep=False)
        ]["InvoiceNo_Tipo"]
        .value_counts()
    )

    print("\nDuplicados por Quantity:")

    print(
        df[
            df.duplicated(keep=False)
        ]["Quantity"]
        .value_counts()
        .head(10)
    )

    print("\nRegistros con UnitPrice negativo:")

    print(
        df[
            df["UnitPrice"] < 0
        ][
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "UnitPrice",
                "CustomerID"
            ]
        ]
    )

    print("\nProductos con más de una Description:")

    productos_descripcion = (
        df.groupby("StockCode")["Description"]
        .nunique(dropna=True)
    )

    print(
        (productos_descripcion > 1).sum()
    )

    print("\nStockCode con Description:")

    print(
        df.groupby("StockCode")["Description"]
        .count()
        .gt(0)
        .sum()
    )

    print(
        "\nEjemplos de StockCode "
        "con múltiples Description:"
    )

    productos_multiples = (
        df.groupby("StockCode")["Description"]
        .nunique(dropna=True)
    )

    codigos = productos_multiples[
        productos_multiples > 1
    ].index[:10]

    print(
        df[
            df["StockCode"].isin(codigos)
        ][
            [
                "StockCode",
                "Description"
            ]
        ]
        .drop_duplicates()
        .sort_values("StockCode")
        .to_string(index=False)
    )

    print("\nTipo de Invoice:")

    print(
        df["InvoiceNo_Tipo"].value_counts()
    )


# ============================================================
# DIMENSIÓN PRODUCTO
# ============================================================

def crear_dim_product(
    df: pd.DataFrame
) -> pd.DataFrame:

    productos = df[
        [
            "StockCode",
            "Description"
        ]
    ].copy()

    productos["StockCode"] = (
        productos["StockCode"]
        .astype(str)
        .str.strip()
        .replace(
            ["nan", "None", ""],
            np.nan
        )
    )

    productos["Description"] = (
        productos["Description"]
        .astype(str)
        .str.strip()
        .replace(
            ["nan", "None", ""],
            np.nan
        )
    )

    descripciones = (
        productos
        .dropna(subset=["StockCode"])
        .groupby("StockCode")["Description"]
        .apply(
            lambda s: " | ".join(
                sorted(
                    s.dropna().unique()
                )
            )
            if s.notna().any()
            else np.nan
        )
        .reset_index(
            name="Description_Completa"
        )
    )

    descripcion_principal = (
        productos
        .dropna(
            subset=[
                "StockCode",
                "Description"
            ]
        )
        .groupby("StockCode")["Description"]
        .agg(
            lambda s: s.value_counts().idxmax()
        )
        .reset_index(
            name="Description_Principal"
        )
    )

    dim_product = descripciones.merge(
        descripcion_principal,
        on="StockCode",
        how="left"
    )

    dim_product = dim_product[
        [
            "StockCode",
            "Description_Principal",
            "Description_Completa"
        ]
    ]

    dim_product.insert(
        0,
        "product_key",
        range(
            1,
            len(dim_product) + 1
        )
    )

    return dim_product


# ============================================================
# ANÁLISIS CUSTOMER ID
# ============================================================

def analizar_customerid_nulo(
    df: pd.DataFrame
):

    clientes_conocidos = df[
        df["CustomerID"].notna()
    ][
        [
            "InvoiceNo",
            "StockCode",
            "CustomerID"
        ]
    ].copy()

    clientes_nulos = df[
        df["CustomerID"].isna()
    ][
        [
            "InvoiceNo",
            "StockCode",
            "CustomerID"
        ]
    ].copy()

    coincidencias = clientes_nulos.merge(
        clientes_conocidos,
        on=[
            "InvoiceNo",
            "StockCode"
        ],
        how="left",
        suffixes=(
            "_nulo",
            "_conocido"
        )
    )

    encontrados = coincidencias[
        coincidencias[
            "CustomerID_conocido"
        ].notna()
    ]

    print(
        f"Registros con CustomerID nulo: "
        f"{len(clientes_nulos):,}"
    )

    print(
        f"Registros nulos con coincidencia: "
        f"{len(encontrados):,}"
    )

    print("\nEjemplos de coincidencias:")

    print(
        encontrados[
            [
                "InvoiceNo",
                "StockCode",
                "CustomerID_conocido"
            ]
        ].head(20)
    )

    return coincidencias


def analizar_customerid_por_invoice(
    df: pd.DataFrame
):

    clientes_conocidos = (
        df[
            df["CustomerID"].notna()
        ][
            [
                "InvoiceNo",
                "CustomerID"
            ]
        ]
        .drop_duplicates()
    )

    clientes_nulos = df[
        df["CustomerID"].isna()
    ][
        [
            "InvoiceNo",
            "StockCode",
            "Description"
        ]
    ].copy()

    coincidencias = clientes_nulos.merge(
        clientes_conocidos,
        on="InvoiceNo",
        how="left"
    )

    encontrados = coincidencias[
        coincidencias["CustomerID"].notna()
    ]

    print(
        f"Registros con CustomerID nulo: "
        f"{len(clientes_nulos):,}"
    )

    print(
        "Registros nulos con coincidencia "
        "por InvoiceNo: "
        f"{len(encontrados):,}"
    )

    print("\nEjemplos:")

    print(
        encontrados[
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "CustomerID"
            ]
        ].head(20)
    )

    return coincidencias


def analizar_customerid_nulo_por_tipo(
    df: pd.DataFrame
):

    customerid_nulos = df[
        df["CustomerID"].isna()
    ].copy()

    resumen = (
        customerid_nulos["InvoiceNo_Tipo"]
        .value_counts()
        .rename_axis("InvoiceNo_Tipo")
        .reset_index(
            name="Cantidad"
        )
    )

    print(
        "\nCustomerID nulo "
        "por tipo de Invoice:"
    )

    print(resumen)

    print("\nPorcentaje:")

    print(
        customerid_nulos[
            "InvoiceNo_Tipo"
        ]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )

    return resumen


def analizar_customerid(
    df: pd.DataFrame
):

    customerid_conocidos = (
        df["CustomerID"]
        .dropna()
        .nunique()
    )

    customerid_nulos = (
        df["CustomerID"]
        .isna()
        .sum()
    )

    print(
        f"\nCustomerID distintos conocidos: "
        f"{customerid_conocidos:,}"
    )

    print(
        f"Registros con CustomerID nulo: "
        f"{customerid_nulos:,}"
    )

    return customerid_conocidos


def crear_dim_customer(
    df: pd.DataFrame
) -> pd.DataFrame:

    dim_customer = (
        df[["CustomerID"]]
        .dropna()
        .drop_duplicates()
        .sort_values("CustomerID")
        .reset_index(drop=True)
    )

    dim_customer.insert(
        0,
        "customer_key",
        range(
            1,
            len(dim_customer) + 1
        )
    )

    return dim_customer


# ============================================================
# DIMENSIÓN FECHA
# ============================================================

def analizar_fecha(
    df: pd.DataFrame
):

    fechas = df["InvoiceDate"]

    print("\nAnálisis de InvoiceDate:")

    print(
        f"Fecha mínima: {fechas.min()}"
    )

    print(
        f"Fecha máxima: {fechas.max()}"
    )

    print(
        f"Fechas distintas: "
        f"{fechas.nunique():,}"
    )

    print(
        f"Fechas nulas: "
        f"{fechas.isna().sum():,}"
    )

    fechas_dia = fechas.dt.normalize()

    print(
        f"Días distintos: "
        f"{fechas_dia.nunique():,}"
    )

    return fechas


def crear_dim_date(
    df: pd.DataFrame
) -> pd.DataFrame:

    fechas = (
        df["InvoiceDate"]
        .dt.normalize()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    dim_date = pd.DataFrame(
        {
            "date": fechas
        }
    )

    dim_date.insert(
        0,
        "date_key",
        dim_date["date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dim_date["year"] = (
        dim_date["date"].dt.year
    )

    dim_date["month"] = (
        dim_date["date"].dt.month
    )

    dim_date["month_name"] = (
        dim_date["date"].dt.month_name()
    )

    dim_date["day"] = (
        dim_date["date"].dt.day
    )

    dim_date["day_of_week"] = (
        dim_date["date"].dt.dayofweek + 1
    )

    return dim_date


# ============================================================
# DIMENSIÓN PAÍS
# ============================================================

def analizar_country(
    df: pd.DataFrame
):

    paises_distintos = (
        df["Country"].nunique()
    )

    paises_nulos = (
        df["Country"].isna().sum()
    )

    print("\nAnálisis de Country:")

    print(
        f"Países distintos: "
        f"{paises_distintos:,}"
    )

    print(
        f"Países nulos: "
        f"{paises_nulos:,}"
    )

    print("\nPaíses:")

    print(
        df["Country"]
        .dropna()
        .sort_values()
        .unique()
    )

    return paises_distintos


def crear_dim_country(
    df: pd.DataFrame
) -> pd.DataFrame:

    dim_country = (
        df[["Country"]]
        .drop_duplicates()
        .sort_values("Country")
        .reset_index(drop=True)
    )

    dim_country.insert(
        0,
        "country_key",
        range(
            1,
            len(dim_country) + 1
        )
    )

    return dim_country


# ============================================================
# FACT SALES - ANÁLISIS
# ============================================================

def analizar_fact_sales(
    df: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_country: pd.DataFrame
):

    fact = df.copy()

    filas_originales = len(fact)

    fact = fact.merge(
        dim_product[
            [
                "product_key",
                "StockCode"
            ]
        ],
        on="StockCode",
        how="left"
    )

    print(
        f"\nDespués de dim_product: "
        f"{len(fact):,} filas"
    )

    fact = fact.merge(
        dim_customer[
            [
                "customer_key",
                "CustomerID"
            ]
        ],
        on="CustomerID",
        how="left"
    )

    print(
        f"Después de dim_customer: "
        f"{len(fact):,} filas"
    )

    fact["date"] = (
        fact["InvoiceDate"]
        .dt.normalize()
    )

    fact = fact.merge(
        dim_date[
            [
                "date_key",
                "date"
            ]
        ],
        on="date",
        how="left"
    )

    print(
        f"Después de dim_date: "
        f"{len(fact):,} filas"
    )

    fact = fact.merge(
        dim_country[
            [
                "country_key",
                "Country"
            ]
        ],
        on="Country",
        how="left"
    )

    print(
        f"Después de dim_country: "
        f"{len(fact):,} filas"
    )

    print(
        f"\nFilas originales: "
        f"{filas_originales:,}"
    )

    print(
        f"Filas finales:    "
        f"{len(fact):,}"
    )

    return fact


# ============================================================
# FACT SALES
# ============================================================

def crear_fact_sales(
    df: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_country: pd.DataFrame
) -> pd.DataFrame:

    fact = df.copy()

    # --------------------------------------------------------
    # Normalizar StockCode
    # --------------------------------------------------------

    fact["StockCode"] = (
        fact["StockCode"]
        .astype(str)
        .str.strip()
        .replace(
            ["nan", "None", ""],
            np.nan
        )
    )

    dim_product_merge = dim_product.copy()

    dim_product_merge["StockCode"] = (
        dim_product_merge["StockCode"]
        .astype(str)
        .str.strip()
        .replace(
            ["nan", "None", ""],
            np.nan
        )
    )

    # --------------------------------------------------------
    # Producto
    # --------------------------------------------------------

    fact = fact.merge(
        dim_product_merge[
            [
                "product_key",
                "StockCode"
            ]
        ],
        on="StockCode",
        how="left"
    )

    productos_sin_key = (
        fact["product_key"]
        .isna()
        .sum()
    )

    print(
        f"\nStockCode sin product_key: "
        f"{productos_sin_key:,}"
    )

    if productos_sin_key > 0:

        print(
            "\nEjemplos de StockCode "
            "sin product_key:"
        )

        print(
            fact.loc[
                fact["product_key"].isna(),
                [
                    "InvoiceNo",
                    "StockCode",
                    "Description",
                    "Quantity",
                    "UnitPrice"
                ]
            ].head(20)
        )

    # --------------------------------------------------------
    # Cliente
    # --------------------------------------------------------

    fact = fact.merge(
        dim_customer[
            [
                "customer_key",
                "CustomerID"
            ]
        ],
        on="CustomerID",
        how="left"
    )

    fact["customer_key"] = (
        fact["customer_key"]
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Fecha
    # --------------------------------------------------------

    fact["date"] = (
        fact["InvoiceDate"]
        .dt.normalize()
    )

    fact = fact.merge(
        dim_date[
            [
                "date_key",
                "date"
            ]
        ],
        on="date",
        how="left"
    )

    # --------------------------------------------------------
    # País
    # --------------------------------------------------------

    fact = fact.merge(
        dim_country[
            [
                "country_key",
                "Country"
            ]
        ],
        on="Country",
        how="left"
    )

    # --------------------------------------------------------
    # Métrica de venta
    # --------------------------------------------------------

    fact["total_amount"] = (
        fact["Quantity"]
        * fact["UnitPrice"]
    )

    # --------------------------------------------------------
    # Columnas finales
    # --------------------------------------------------------

    fact_sales = fact[
        [
            "InvoiceNo",
            "product_key",
            "customer_key",
            "date_key",
            "country_key",
            "Quantity",
            "UnitPrice",
            "total_amount"
        ]
    ].copy()

    return fact_sales