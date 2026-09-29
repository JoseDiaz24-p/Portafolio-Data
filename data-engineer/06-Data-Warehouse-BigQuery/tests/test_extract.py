from src.extract import extract_data,DATA_RAW


def test_extract_data():
    df = extract_data(DATA_RAW)

    print(df.head())
    print(f"filas: {len(df)}:,")
    print(f"columnas: {len(df.columns)}")
    