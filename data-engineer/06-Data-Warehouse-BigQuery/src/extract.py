import os
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_RAW = os.path.join(
    BASE_DIR,
    "data",
    "Online Retail.xlsx"
)


# ============================================================
# EXTRACT
# ============================================================

def extract_data(ruta: str) -> pd.DataFrame:

    print(f"Extrayendo Datos Desde: {ruta}")

    if not os.path.exists(ruta):
        print(f"No se encontró el dataset en: {ruta}")

        raise FileNotFoundError(
            f"Archivo no disponible: {ruta}"
        )

    df = pd.read_excel(ruta)

    print(
        f"-> Registros extraídos: "
        f"{len(df):,}"
    )

    return df