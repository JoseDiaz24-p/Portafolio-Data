from pathlib import Path
import pandas as pd


OUTPUT_DIR = Path("output")


def guardar_csv(df: pd.DataFrame, nombre_archivo: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ruta = OUTPUT_DIR / nombre_archivo

    df.to_csv(ruta, index=False)

    return ruta