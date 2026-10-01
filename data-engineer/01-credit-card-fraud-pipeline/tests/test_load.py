import sqlite3

import pandas as pd

from src.load import load_data


def test_load_crea_tabla_y_vistas(tmp_path):
    df = pd.DataFrame({
        "transaction_id": ["tx_001", "tx_002"],
        "amount": [100, 500],
        "is_fraud": [0, 1],
        "merchant_category": [
            "Food",
            "Travel"
        ],
        "rango_monto": [
            "Medio (50-200)",
            "Alto (200-1000)"
        ],
        "tipo_transaccion": [
            "Legítima",
            "Fraude"
        ]
    })

    db_path = tmp_path / "test_fraud.db"

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
        "SELECT COUNT(*) FROM transacciones_bancarias"
    ).fetchone()[0]

    conn.close()

    objects = set(objects)

    assert (
        "transacciones_bancarias",
        "table"
    ) in objects

    assert (
        "v_resumen_categoria",
        "view"
    ) in objects

    assert (
        "v_resumen_riesgo",
        "view"
    ) in objects

    assert row_count == 2