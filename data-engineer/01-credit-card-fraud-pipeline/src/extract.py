import logging
import os

import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_RAW = os.path.join(
    BASE_DIR,
    "data",
    "credit_card.csv"
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "registro_fraudes.log"
)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("fraud_pipeline")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )

        console_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def extract_data(ruta: str) -> pd.DataFrame:
    logger = get_logger()

    logger.info(
        f"[1/3] Extrayendo datos desde: {ruta}"
    )

    if not os.path.exists(ruta):
        logger.error(
            f"No se encontró el dataset en: {ruta}"
        )

        raise FileNotFoundError(
            f"Archivo no disponible: {ruta}"
        )

    df = pd.read_csv(ruta)

    logger.info(
        f"-> Registros extraídos: {len(df):,}"
    )

    return df