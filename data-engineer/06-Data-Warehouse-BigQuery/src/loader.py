from google.cloud import bigquery
import pandas as pd


# ============================================================
# BIGQUERY CLIENT
# ============================================================

def crear_cliente_bigquery(
    project_id: str
) -> bigquery.Client:

    client = bigquery.Client(
        project=project_id
    )

    return client


# ============================================================
# LOAD DATAFRAME
# ============================================================

def cargar_dataframe(
    client: bigquery.Client,
    df: pd.DataFrame,
    table_id: str,
    schema: list
):

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=(
            bigquery.WriteDisposition.WRITE_TRUNCATE
        )
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )

    job.result()

    print(
        f"Tabla cargada correctamente: "
        f"{table_id}"
    )

    print(
        f"Registros cargados: "
        f"{len(df):,}"
    )