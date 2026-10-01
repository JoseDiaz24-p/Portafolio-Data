from src.extract import DATA_RAW, get_logger, extract_data
from src.transform import transform_data
from src.load import load_data


def main() -> None:
    logger = get_logger()

    logger.info("Iniciando pipeline de fraude...")

    # ----------------------------------------------------
    # 1. Extract
    # ----------------------------------------------------

    df = extract_data(DATA_RAW)

    # ----------------------------------------------------
    # 2. Transform
    # ----------------------------------------------------

    df_transformado = transform_data(df)

    # ----------------------------------------------------
    # 3. Load
    # ----------------------------------------------------

    db_path = "fraud_warehouse.db"

    load_data(
        df_transformado,
        db_path
    )

    logger.info(
        "Pipeline de fraude ejecutado exitosamente."
    )


if __name__ == "__main__":
    main()