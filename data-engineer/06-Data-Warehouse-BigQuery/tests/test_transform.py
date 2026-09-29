from src.extract import extract_data, DATA_RAW
from src.transform import (
    transformar_datos,
    crear_dim_product,
    analizar_customerid_nulo,
    analizar_customerid_por_invoice,
    analizar_customerid_nulo_por_tipo,
    analizar_customerid,
    crear_dim_customer,
    analizar_fecha,
    crear_dim_date,
    analizar_country,
    crear_dim_country,
    analizar_fact_sales,
    crear_fact_sales
)


def test_transform_data():

    df = extract_data(DATA_RAW)

    df_transformado = transformar_datos(df)

    assert "InvoiceNo_Tipo" in df_transformado.columns
    assert "Cancelacion" in df_transformado["InvoiceNo_Tipo"].values
    assert "Venta Normal" in df_transformado["InvoiceNo_Tipo"].values

    dim_product = crear_dim_product(df_transformado)

    assert "StockCode" in dim_product.columns
    assert "Description_Principal" in dim_product.columns
    assert "Description_Completa" in dim_product.columns

    assert dim_product["StockCode"].is_unique

    analizar_customerid_nulo(df_transformado)

    analizar_customerid_por_invoice(df_transformado)

    analizar_customerid_nulo_por_tipo(df_transformado)

    analizar_customerid(df_transformado)


    dim_customer = crear_dim_customer(df_transformado)

    assert "customer_key" in dim_customer.columns
    assert "CustomerID" in dim_customer.columns

    assert dim_customer["customer_key"].is_unique
    assert dim_customer["CustomerID"].is_unique

    assert len(dim_customer) == 4372

    analizar_fecha(df_transformado)

    dim_date = crear_dim_date(df_transformado)

    assert "date_key" in dim_date.columns
    assert "date" in dim_date.columns
    assert "year" in dim_date.columns
    assert "month" in dim_date.columns
    assert "month_name" in dim_date.columns
    assert "day" in dim_date.columns
    assert "day_of_week" in dim_date.columns

    assert dim_date["date_key"].is_unique
    assert dim_date["date"].is_unique

    assert len(dim_date) == 305

    analizar_country(df_transformado)

    dim_country = crear_dim_country(df_transformado)

    assert "country_key" in dim_country.columns
    assert "Country" in dim_country.columns

    assert dim_country["country_key"].is_unique
    assert dim_country["Country"].is_unique

    assert len(dim_country) == 38

    fact = analizar_fact_sales(
    df_transformado,
    dim_product,
    dim_customer,
    dim_date,
    dim_country
    )

    assert len(fact) == len(df_transformado)
    fact_sales = crear_fact_sales(
        df_transformado,
        dim_product,
        dim_customer,
        dim_date,
        dim_country
    )

    assert len(fact_sales) == 541909

    assert "InvoiceNo" in fact_sales.columns
    assert "product_key" in fact_sales.columns
    assert "customer_key" in fact_sales.columns
    assert "date_key" in fact_sales.columns
    assert "country_key" in fact_sales.columns
    assert "Quantity" in fact_sales.columns
    assert "UnitPrice" in fact_sales.columns
    assert "total_amount" in fact_sales.columns

    assert fact_sales["product_key"].notna().all()
    assert fact_sales["date_key"].notna().all()
    assert fact_sales["country_key"].notna().all()

    assert fact_sales["customer_key"].notna().all()