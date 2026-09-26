from src.analytics import (
    conectar_duckdb,
    viajes_por_proveedor,
    distancia_promedio_por_proveedor,
    ingreso_metodo_de_pago,
    resumen_general,
)


def test_viajes_por_proveedor():
    conexion = conectar_duckdb()

    try:
        resultado = viajes_por_proveedor(conexion)

        assert not resultado.empty
        assert "VendorID" in resultado.columns
        assert "cantidad_viajes" in resultado.columns
        assert resultado["cantidad_viajes"].sum() == 3724889

    finally:
        conexion.close()


def test_distancia_promedio_por_proveedor():
    conexion = conectar_duckdb()

    try:
        resultado = distancia_promedio_por_proveedor(conexion)

        assert not resultado.empty
        assert "VendorID" in resultado.columns
        assert "distancia_promedio" in resultado.columns
        assert resultado["distancia_promedio"].notna().all()

    finally:
        conexion.close()


def test_ingreso_metodo_de_pago():
    conexion = conectar_duckdb()

    try:
        resultado = ingreso_metodo_de_pago(conexion)

        assert not resultado.empty
        assert "payment_type" in resultado.columns
        assert "cantidad_viajes" in resultado.columns
        assert "monto_acumulado" in resultado.columns

    finally:
        conexion.close()


def test_resumen_general():
    conexion = conectar_duckdb()

    try:
        resultado = resumen_general(conexion)

        assert len(resultado) == 1
        assert resultado["total_viajes"].iloc[0] == 3724889
        assert resultado["distancia_promedio"].iloc[0] == 6.46

    finally:
        conexion.close()