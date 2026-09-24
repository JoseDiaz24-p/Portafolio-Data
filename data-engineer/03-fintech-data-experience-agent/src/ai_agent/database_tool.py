import os
import sqlite3
from typing import Dict, Any


def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Obtiene las métricas financieras, de actividad y segmento
    de un cliente desde la base analítica de la billetera digital.

    Args:
        customer_id: Identificador único del cliente.
    """

    directorio_proyecto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    db_path = os.path.join(
        directorio_proyecto,
        "database",
        "mach_analytics.db"
    )

    customer_id = customer_id.strip()

    if not customer_id:
        return {"error": "El Customer_ID no puede estar vacío."}

    if not os.path.exists(db_path):
        return {
            "error": f"No se encontró la base de datos en: {db_path}"
        }

    query = """
        SELECT
            Customer_ID,
            Age,
            Location,
            Income_Level,
            Total_Transactions,
            Avg_Transaction_Value,
            Total_Spent,
            Active_Days,
            Daily_Spend_Rate,
            Ticket_Spread,
            Customer_Segment
        FROM dim_customers_ltv
        WHERE Customer_ID = ?;
    """

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (customer_id,))
            row = cursor.fetchone()

    except sqlite3.Error as error:
        return {
            "error": f"Error al consultar la base de datos: {error}"
        }

    if not row:
        return {
            "error": (
                f"No se encontraron registros para el cliente "
                f"'{customer_id}'."
            )
        }

    columnas = [
        "Customer_ID",
        "Age",
        "Location",
        "Income_Level",
        "Total_Transactions",
        "Avg_Transaction_Value",
        "Total_Spent",
        "Active_Days",
        "Daily_Spend_Rate",
        "Ticket_Spread",
        "Customer_Segment"
    ]

    return dict(zip(columnas, row))