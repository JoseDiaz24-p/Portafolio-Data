from src.extract import extract_data, DATA_RAW

from src.transform import (
    transformar_datos,
    crear_dim_product,
    crear_dim_customer,
    crear_dim_date,
    crear_dim_country,
    crear_fact_sales
)

from src.loader import (
    crear_cliente_bigquery,
    cargar_dataframe
)

from src.schema import (
    DIM_PRODUCT_SCHEMA,
    DIM_CUSTOMER_SCHEMA,
    DIM_DATE_SCHEMA,
    DIM_COUNTRY_SCHEMA,
    FACT_SALES_SCHEMA
)


PROJECT_ID = "data-engenieer"
DATASET_ID = "online_retail_dw"


def main():

    print("=" * 60)
    print("INICIO DEL DATA WAREHOUSE PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. EXTRACT
    # ---------------------------------------------------------

    df = extract_data(DATA_RAW)

    # ---------------------------------------------------------
    # 2. TRANSFORM
    # ---------------------------------------------------------

    df = transformar_datos(df)

    print("\nCreando dimensiones...")

    dim_product = crear_dim_product(df)
    dim_customer = crear_dim_customer(df)
    dim_date = crear_dim_date(df)
    dim_country = crear_dim_country(df)

    print(f"-> dim_product:  {len(dim_product):,}")
    print(f"-> dim_customer: {len(dim_customer):,}")
    print(f"-> dim_date:     {len(dim_date):,}")
    print(f"-> dim_country:  {len(dim_country):,}")

    print("\nCreando fact_sales...")

    fact_sales = crear_fact_sales(
        df,
        dim_product,
        dim_customer,
        dim_date,
        dim_country
    )

    print(f"-> fact_sales:   {len(fact_sales):,}")

    # ---------------------------------------------------------
    # 3. BIGQUERY
    # ---------------------------------------------------------

    print("\nConectando con BigQuery...")

    client = crear_cliente_bigquery(PROJECT_ID)

    # ---------------------------------------------------------
    # 4. LOAD - DIMENSIONES
    # ---------------------------------------------------------

    print("\nCargando dimensiones...")

    cargar_dataframe(
        client,
        dim_product,
        f"{PROJECT_ID}.{DATASET_ID}.dim_product",
        DIM_PRODUCT_SCHEMA
    )

    cargar_dataframe(
        client,
        dim_customer,
        f"{PROJECT_ID}.{DATASET_ID}.dim_customer",
        DIM_CUSTOMER_SCHEMA
    )

    cargar_dataframe(
        client,
        dim_date,
        f"{PROJECT_ID}.{DATASET_ID}.dim_date",
        DIM_DATE_SCHEMA
    )

    cargar_dataframe(
        client,
        dim_country,
        f"{PROJECT_ID}.{DATASET_ID}.dim_country",
        DIM_COUNTRY_SCHEMA
    )

    # ---------------------------------------------------------
    # 5. LOAD - FACT
    # ---------------------------------------------------------

    print("\nCargando fact_sales...")

    cargar_dataframe(
        client,
        fact_sales,
        f"{PROJECT_ID}.{DATASET_ID}.fact_sales",
        FACT_SALES_SCHEMA
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()