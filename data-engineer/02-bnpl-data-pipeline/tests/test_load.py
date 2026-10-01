import sqlite3

import pandas as pd

from src.load import load_data


def test_load_crea_tabla_y_vistas(tmp_path):
    df = pd.DataFrame({
        "Transaction_ID": [
            "tx_001",
            "tx_002",
            "tx_003"
        ],
        "Customer_ID": [
            "cust_001",
            "cust_002",
            "cust_003"
        ],
        "Age": [
            22,
            35,
            65
        ],
        "Income": [
            3000,
            4500,
            5000
        ],
        "Purchase_Amount": [
            100,
            500,
            1500
        ],
        "Credit_Score": [
            650,
            720,
            800
        ],
        "BNPL_Provider": [
            "Klarna",
            "Afterpay",
            "Affirm"
        ],
        "Purchase_Category": [
            "Fashion",
            "Electronics",
            "Travel"
        ],
        "Repayment_Status": [
            "Paid",
            "Defaulted",
            "Paid"
        ],
        "rango_edad": [
            "Joven (18-25)",
            "Adulto Joven (26-40)",
            "Senior (>60)"
        ]
    })

    db_path = tmp_path / "test_bnpl.db"

    load_data(
        df,
        str(db_path)
    )

    conn = sqlite3.connect(db_path)

    objects = conn.execute(
        """
        SELECT name, type
        FROM sqlite_master
        WHERE type IN ('table', 'view')
        """
    ).fetchall()

    row_count = conn.execute(
        "SELECT COUNT(*) FROM clientes_credito"
    ).fetchone()[0]

    conn.close()

    objects = set(objects)

    # Tabla principal
    assert (
        "clientes_credito",
        "table"
    ) in objects

    # Vistas analíticas
    assert (
        "v_riesgo_por_edad",
        "view"
    ) in objects

    assert (
        "v_riesgo_por_proveedor",
        "view"
    ) in objects

    assert (
        "v_riesgo_por_categoria",
        "view"
    ) in objects

    # Verificar cantidad de registros cargados
    assert row_count == 3