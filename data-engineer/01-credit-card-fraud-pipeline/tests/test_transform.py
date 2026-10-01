import pandas as pd

from src.transform import transform_data


def test_transform_elimina_montos_invalidos():
    df = pd.DataFrame({
        "transaction_id": ["tx_001", "tx_002", "tx_003"],
        "amount": [100, 0, 250],
        "is_fraud": [0, 1, 0],
        "merchant_category": [
            "Food",
            "Grocery",
            "Travel"
        ]
    })

    result = transform_data(df)

    assert len(result) == 2
    assert (result["amount"] > 0).all()


def test_transform_elimina_duplicados():
    df = pd.DataFrame({
        "transaction_id": [
            "tx_001",
            "tx_001",
            "tx_002"
        ],
        "amount": [100, 100, 200],
        "is_fraud": [0, 0, 1],
        "merchant_category": [
            "Food",
            "Food",
            "Travel"
        ]
    })

    result = transform_data(df)

    assert len(result) == 2
    assert result["transaction_id"].is_unique


def test_transform_crea_columnas_derivadas():
    df = pd.DataFrame({
        "transaction_id": ["tx_001", "tx_002"],
        "amount": [25, 1500],
        "is_fraud": [0, 1],
        "merchant_category": [
            "Food",
            "Electronics"
        ]
    })

    result = transform_data(df)

    assert "rango_monto" in result.columns
    assert "tipo_transaccion" in result.columns

    assert result.loc[
        result["transaction_id"] == "tx_001",
        "tipo_transaccion"
    ].iloc[0] == "Legítima"

    assert result.loc[
        result["transaction_id"] == "tx_002",
        "tipo_transaccion"
    ].iloc[0] == "Fraude"