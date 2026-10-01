import sqlite3

from src.extract import get_logger


def generate_reports(db_path: str) -> None:
    logger = get_logger()

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        # ----------------------------------------------------
        # Reporte por edad
        # ----------------------------------------------------

        logger.info(
            "--- REPORTE DE INCUMPLIMIENTO POR EDAD ---"
        )

        reporte_edad = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_edad
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_edad:
            logger.info(
                f"Grupo: {fila[0]:<22} | "
                f"Clientes: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Compra promedio: ${fila[4]:,.2f}"
            )

        # ----------------------------------------------------
        # Reporte por proveedor
        # ----------------------------------------------------

        logger.info(
            "--- REPORTE DE INCUMPLIMIENTO POR PROVEEDOR ---"
        )

        reporte_proveedor = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_proveedor
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_proveedor:
            logger.info(
                f"Proveedor: {fila[0]:<10} | "
                f"Operaciones: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Monto: ${fila[4]:,.2f}"
            )

        # ----------------------------------------------------
        # Reporte por categoría
        # ----------------------------------------------------

        logger.info(
            "--- REPORTE DE INCUMPLIMIENTO POR CATEGORÍA ---"
        )

        reporte_categoria = cursor.execute("""
            SELECT *
            FROM v_riesgo_por_categoria
            ORDER BY tasa_incumplimiento_porcentaje DESC
        """).fetchall()

        for fila in reporte_categoria:
            logger.info(
                f"Categoría: {fila[0]:<18} | "
                f"Operaciones: {fila[1]:<6} | "
                f"Incumplimientos: {fila[2]:<5} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Compra promedio: ${fila[4]:,.2f} | "
                f"Monto total: ${fila[5]:,.2f}"
            )

    finally:
        conn.close()