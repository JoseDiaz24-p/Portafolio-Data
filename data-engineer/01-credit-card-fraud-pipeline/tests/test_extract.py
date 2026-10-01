import pandas as pd

from src.extract import extract_data


def test_extract_data_carga_csv():
    df = extract_data("data/credit_card.csv")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10000
    assert "transaction_id" in df.columns
    assert "amount" in df.columns
    assert "is_fraud" in df.columns