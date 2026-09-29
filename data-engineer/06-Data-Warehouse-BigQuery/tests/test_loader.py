
from src.extract import extract_data, DATA_RAW
from src.transform import (
    transformar_datos,
    crear_dim_product
)
from src.loader import (
    crear_cliente_bigquery,
    cargar_dataframe
)
from src.schema import DIM_PRODUCT_SCHEMA


PROJECT_ID = "data-engenieer"

TABLE_ID = (
    "data-engenieer."
    "online_retail_dw."
    "dim_product"
)


df = extract_data(DATA_RAW)

df = transformar_datos(df)

dim_product = crear_dim_product(df)

print("\nDimensión de productos:")
print(dim_product.head())

print(f"\nRegistros: {len(dim_product):,}")

client = crear_cliente_bigquery(PROJECT_ID)

cargar_dataframe(
    client=client,
    df=dim_product,
    table_id=TABLE_ID,
    schema=DIM_PRODUCT_SCHEMA
)