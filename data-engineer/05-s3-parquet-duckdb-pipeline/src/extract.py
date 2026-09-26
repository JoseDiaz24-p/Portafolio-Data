import duckdb
import pandas as pd


S3_PATH = (
    "s3://portfolio-data-engineering-jose-2026/"
    "yellow_tripdata_2026-01.parquet"
)


def conectar_duckdb():
    """
    Crea una conexión con DuckDB y configura
    el acceso a Amazon S3.
    """

    conexion = duckdb.connect()

    conexion.execute("INSTALL httpfs;")
    conexion.execute("LOAD httpfs;")

    return conexion


def extraer_datos() -> pd.DataFrame:
    """
    Lee el archivo Parquet desde Amazon S3
    utilizando DuckDB y devuelve un DataFrame.
    """

    conexion = conectar_duckdb()

    try:

        consulta = f"""
            SELECT *
            FROM read_parquet('{S3_PATH}')
        """

        df = conexion.execute(consulta).df()

        return df

    finally:

        conexion.close()