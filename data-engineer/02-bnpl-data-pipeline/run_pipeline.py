import os

from src.analytics import generate_reports
from src.extract import DATA_RAW, extract_data, get_logger
from src.load import load_data
from src.transform import transform_data


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_OUTPUT = os.path.join(
    BASE_DIR,
    "bnpl_analytics.db"
)


logger = get_logger()


def run_pipeline() -> None:
    try:
        logger.info(
            "Iniciando pipeline BNPL..."
        )

        raw_df = extract_data(
            DATA_RAW
        )

        clean_df = transform_data(
            raw_df
        )

        load_data(
            clean_df,
            DB_OUTPUT
        )

        generate_reports(
            DB_OUTPUT
        )

        logger.info(
            "Pipeline BNPL ejecutado exitosamente."
        )

    except Exception as error:
        logger.critical(
            f"Error en el pipeline: {error}"
        )
        raise


if __name__ == "__main__":
    run_pipeline()