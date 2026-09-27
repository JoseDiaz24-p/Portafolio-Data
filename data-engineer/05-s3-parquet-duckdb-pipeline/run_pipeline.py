from src.extract import extraer_datos
from src.transform import transformar_datos


def main():

    print("[1/2] Extractayendo Datos...")
    df = extraer_datos()
    print(f"Datos Extraidos: {len(df)}")

    print("[2/2] Transformando Datos...")
    df = transformar_datos(df)
    print(f"Registrando Los Datos: {len(df)}")


if __name__ == "__main__":
    main()