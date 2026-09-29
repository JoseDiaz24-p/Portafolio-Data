from google.cloud import bigquery


# ============================================================
# DIM PRODUCT
# ============================================================

DIM_PRODUCT_SCHEMA = [
    bigquery.SchemaField(
        "product_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "StockCode",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "Description_Principal",
        "STRING",
        mode="NULLABLE"
    ),
    bigquery.SchemaField(
        "Description_Completa",
        "STRING",
        mode="NULLABLE"
    ),
]


# ============================================================
# DIM CUSTOMER
# ============================================================

DIM_CUSTOMER_SCHEMA = [
    bigquery.SchemaField(
        "customer_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "CustomerID",
        "INT64",
        mode="REQUIRED"
    ),
]


# ============================================================
# DIM DATE
# ============================================================

DIM_DATE_SCHEMA = [
    bigquery.SchemaField(
        "date_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "date",
        "DATE",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "year",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "month",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "month_name",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "day",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "day_of_week",
        "INT64",
        mode="REQUIRED"
    ),
]


# ============================================================
# DIM COUNTRY
# ============================================================

DIM_COUNTRY_SCHEMA = [
    bigquery.SchemaField(
        "country_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "Country",
        "STRING",
        mode="REQUIRED"
    ),
]


# ============================================================
# FACT SALES
# ============================================================

FACT_SALES_SCHEMA = [
    bigquery.SchemaField(
        "InvoiceNo",
        "STRING",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "product_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "customer_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "date_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "country_key",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "Quantity",
        "INT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "UnitPrice",
        "FLOAT64",
        mode="REQUIRED"
    ),
    bigquery.SchemaField(
        "total_amount",
        "FLOAT64",
        mode="REQUIRED"
    ),
]