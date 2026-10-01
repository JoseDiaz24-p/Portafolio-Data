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
        # Eliminar vistas anteriores
        # ----------------------------------------------------

        cursor.execute(
            "DROP VIEW IF EXISTS v_riesgo_por_edad"
        )

        cursor.execute(
            "DROP VIEW IF EXISTS v_riesgo_por_proveedor"
        )

        cursor.execute(
            "DROP VIEW IF EXISTS v_riesgo_por_categoria"
        )

        # ----------------------------------------------------
        # Tabla principal
        # ----------------------------------------------------

        df.to_sql(
            "clientes_credito",
            conn,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Vista: riesgo por edad
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_riesgo_por_edad AS
            SELECT
                rango_edad,
                COUNT(Transaction_ID) AS total_clientes,

                SUM(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_incumplimientos,

                ROUND(
                    AVG(
                        CASE
                            WHEN Repayment_Status = 'Defaulted'
                            THEN 1.0
                            ELSE 0.0
                        END
                    ) * 100,
                    2
                ) AS tasa_incumplimiento_porcentaje,

                ROUND(
                    AVG(Purchase_Amount),
                    2
                ) AS compra_promedio

            FROM clientes_credito

            GROUP BY rango_edad;
        """)

        # ----------------------------------------------------
        # Vista: riesgo por proveedor
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_riesgo_por_proveedor AS
            SELECT
                BNPL_Provider AS proveedor_bnpl,
                COUNT(Transaction_ID) AS total_operaciones,

                SUM(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_incumplimientos,

                ROUND(
                    AVG(
                        CASE
                            WHEN Repayment_Status = 'Defaulted'
                            THEN 1.0
                            ELSE 0.0
                        END
                    ) * 100,
                    2
                ) AS tasa_incumplimiento_porcentaje,

                ROUND(
                    SUM(Purchase_Amount),
                    2
                ) AS monto_total_compras

            FROM clientes_credito

            GROUP BY BNPL_Provider;
        """)

        # ----------------------------------------------------
        # Vista: riesgo por categoría
        # ----------------------------------------------------

        cursor.execute("""
            CREATE VIEW v_riesgo_por_categoria AS
            SELECT
                Purchase_Category AS categoria_compra,
                COUNT(Transaction_ID) AS total_operaciones,

                SUM(
                    CASE
                        WHEN Repayment_Status = 'Defaulted'
                        THEN 1
                        ELSE 0
                    END
                ) AS total_incumplimientos,

                ROUND(
                    AVG(
                        CASE
                            WHEN Repayment_Status = 'Defaulted'
                            THEN 1.0
                            ELSE 0.0
                        END
                    ) * 100,
                    2
                ) AS tasa_incumplimiento_porcentaje,

                ROUND(
                    AVG(Purchase_Amount),
                    2
                ) AS compra_promedio,

                ROUND(
                    SUM(Purchase_Amount),
                    2
                ) AS monto_total_compras

            FROM clientes_credito

            GROUP BY Purchase_Category;
        """)

        conn.commit()

        logger.info(
            "-> Tabla 'clientes_credito' y vistas "
            "analíticas creadas correctamente."
        )

    finally:
        conn.close()