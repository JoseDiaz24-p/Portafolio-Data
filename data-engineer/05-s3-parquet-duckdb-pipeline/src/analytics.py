import duckdb


S3_PATH = (
    "s3://portfolio-data-engineering-jose-2026/"
    "yellow_tripdata_2026-01.parquet"
)


def conectar_duckdb():
    conexion = duckdb.connect()

    conexion.execute("INSTALL httpfs;")
    conexion.execute("LOAD httpfs;")



    return conexion


def viajes_por_proveedor(conexion):
    consulta = f"""
        SELECT
            VendorID,
            COUNT(*) AS cantidad_viajes
        FROM read_parquet('{S3_PATH}')
        GROUP BY VendorID
    """

    return conexion.execute(consulta).df()


def distancia_promedio_por_proveedor(conexion):
    consulta = f"""
        SELECT
            VendorID,
            ROUND(AVG(trip_distance), 2) AS distancia_promedio
        FROM read_parquet('{S3_PATH}')
        GROUP BY VendorID
    """

    return conexion.execute(consulta).df()


def ingreso_metodo_de_pago(conexion):
    consulta = f"""
        SELECT
            payment_type,
            COUNT(*) AS cantidad_viajes,
            SUM(total_amount) AS monto_acumulado
        FROM read_parquet('{S3_PATH}')
        GROUP BY payment_type
    """

    return conexion.execute(consulta).df()


def resumen_general(conexion):
    consulta = f"""
        SELECT
            COUNT(*) AS total_viajes,
            ROUND(AVG(trip_distance), 2) AS distancia_promedio,
            ROUND(SUM(total_amount), 2) AS ingresos_totales,
            ROUND(AVG(total_amount), 2) AS tarifa_promedio
        FROM read_parquet('{S3_PATH}')
    """

    return conexion.execute(consulta).df()