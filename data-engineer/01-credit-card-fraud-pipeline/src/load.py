import sqlite3

import pandas as pd

from src.extract import get_logger


def load_data(
    df: pd.DataFrame,
    db_path: str
) -> None:

    logger = get_logger()

    logger.info(
        "[3/3] Cargando datos en SQLite..."
    )

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        # ----------------------------------------------------
        # Recrear vistas de forma determinista
        # ----------------------------------------------------

        cursor.execute(
            "DROP VIEW IF EXISTS v_resumen_categoria;"
        )

        cursor.execute(
            "DROP VIEW IF EXISTS v_resumen_riesgo;"
        )

        # ----------------------------------------------------
        # Cargar tabla principal
        # ----------------------------------------------------

        df.to_sql(
            "transacciones_bancarias",
            conn,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Vista: resumen por categoría
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_resumen_categoria AS
            SELECT
                merchant_category AS categoria_comercio,
                COUNT(transaction_id) AS total_operaciones,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS total_fraudes,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    / COUNT(transaction_id),
                    2
                ) AS tasa_fraude_porcentaje,

                ROUND(
                    AVG(amount),
                    2
                ) AS ticket_promedio,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN amount
                            ELSE 0
                        END
                    ),
                    2
                ) AS total_defraudado

            FROM transacciones_bancarias

            GROUP BY merchant_category;
        """)

        # ----------------------------------------------------
        # Vista: resumen por rango de monto
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_resumen_riesgo AS
            SELECT
                rango_monto,

                COUNT(transaction_id)
                    AS total_transacciones,

                SUM(
                    CASE
                        WHEN is_fraud = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS casos_fraude,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                    / COUNT(transaction_id),
                    2
                ) AS tasa_fraude_porcentaje,

                ROUND(
                    AVG(amount),
                    2
                ) AS monto_promedio,

                ROUND(
                    SUM(
                        CASE
                            WHEN is_fraud = 1
                            THEN amount
                            ELSE 0
                        END
                    ),
                    2
                ) AS monto_total_defraudado

            FROM transacciones_bancarias

            GROUP BY rango_monto;
        """)

        conn.commit()

        logger.info(
            "-> Tabla y vistas analíticas creadas correctamente."
        )

        # ----------------------------------------------------
        # Reporte por categoría
        # ----------------------------------------------------

        reporte_categoria = cursor.execute(
            """
            SELECT *
            FROM v_resumen_categoria
            ORDER BY tasa_fraude_porcentaje DESC;
            """
        ).fetchall()

        logger.info(
            "\n--- REPORTE DE FRAUDE POR CATEGORÍA ---"
        )

        for fila in reporte_categoria:
            logger.info(
                f"Categoría: {fila[0]:<15} | "
                f"Operaciones: {fila[1]:<5} | "
                f"Fraudes: {fila[2]:<4} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Defraudado: ${fila[5]:,.2f}"
            )

        # ----------------------------------------------------
        # Reporte por rango de monto
        # ----------------------------------------------------

        reporte_riesgo = cursor.execute(
            """
            SELECT *
            FROM v_resumen_riesgo
            ORDER BY tasa_fraude_porcentaje DESC;
            """
        ).fetchall()

        logger.info(
            "\n--- REPORTE DE FRAUDE POR RANGO DE MONTO ---"
        )

        for fila in reporte_riesgo:
            logger.info(
                f"Rango: {fila[0]:<18} | "
                f"Transacciones: {fila[1]:<5} | "
                f"Fraudes: {fila[2]:<4} | "
                f"Tasa: {fila[3]:>6}% | "
                f"Defraudado: ${fila[5]:,.2f}"
            )

    finally:
        conn.close()