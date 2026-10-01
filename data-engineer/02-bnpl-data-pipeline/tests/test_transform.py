import pandas as pd

from src.transform import transform_data


def crear_dataframe_base():
    return pd.DataFrame({
        "Transaction_ID": [
            "TX001",
            "TX002",
            "TX003"
        ],
        "Customer_Age": [
            25,
            35,
            50
        ],
        "Gender": [
            "Male",
            "Female",
            "Male"
        ],
        "Annual_Income": [
            30000,
            45000,
            60000
        ],
        "Credit_Score": [
            700,
            650,
            750
        ],
        "Purchase_Category": [
            "Fashion",
            "Electronics",
            "Travel"
        ],
        "BNPL_Provider": [
            "Klarna",
            "Afterpay",
            "Affirm"
        ],
        "Purchase_Amount": [
            100,
            500,
            1000
        ],
        "Repayment_Status": [
            "Paid On Time",
            "Defaulted",
            "Paid On Time"
        ]
    })


def test_transform_elimina_edades_invalidas():
    df = crear_dataframe_base()

    df.loc[1, "Customer_Age"] = 10

    result = transform_data(df)

    assert len(result) == 2
    assert (result["Customer_Age"] >= 18).all()
    assert (result["Customer_Age"] <= 64).all()


def test_transform_elimina_duplicados():
    df = crear_dataframe_base()

    df = pd.concat(
        [df, df.iloc[[0]]],
        ignore_index=True
    )

    result = transform_data(df)

    assert len(result) == 3
    assert result["Transaction_ID"].is_unique


def test_transform_elimina_montos_invalidos():
    df = crear_dataframe_base()

    df.loc[1, "Purchase_Amount"] = 0

    result = transform_data(df)

    assert len(result) == 2
    assert (result["Purchase_Amount"] > 0).all()


def test_transform_elimina_credit_score_invalido():
    df = crear_dataframe_base()

    df.loc[1, "Credit_Score"] = 900

    result = transform_data(df)

    assert len(result) == 2
    assert (result["Credit_Score"] >= 300).all()
    assert (result["Credit_Score"] <= 849).all()


def test_transform_crea_columnas_derivadas():
    df = crear_dataframe_base()

    result = transform_data(df)

    assert "rango_edad" in result.columns
    assert "nivel_credito" in result.columns
    assert "estado_pago" in result.columns


def test_transform_normaliza_estado_pago():
    df = crear_dataframe_base()

    result = transform_data(df)

    estado = result.loc[
        result["Transaction_ID"] == "TX001",
        "estado_pago"
    ].iloc[0]

    assert estado == "Al Día"