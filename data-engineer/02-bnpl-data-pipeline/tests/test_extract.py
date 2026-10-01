import pandas as pd

from src.extract import extract_data


def test_extract_data_carga_csv(tmp_path):
    csv_path = tmp_path / "bnpl_test.csv"

    df = pd.DataFrame({
        "Transaction_ID": ["TX001", "TX002"],
        "Customer_Age": [25, 35],
        "Gender": ["Male", "Female"],
        "Annual_Income": [30000, 45000],
        "Credit_Score": [700, 650],
        "Purchase_Category": ["Fashion", "Electronics"],
        "BNPL_Provider": ["Klarna", "Afterpay"],
        "Purchase_Amount": [100, 500],
        "Repayment_Status": [
            "Paid On Time",
            "Defaulted"
        ]
    })

    df.to_csv(csv_path, index=False)

    result = extract_data(str(csv_path))

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

    assert list(result.columns) == [
        "Transaction_ID",
        "Customer_Age",
        "Gender",
        "Annual_Income",
        "Credit_Score",
        "Purchase_Category",
        "BNPL_Provider",
        "Purchase_Amount",
        "Repayment_Status"
    ]