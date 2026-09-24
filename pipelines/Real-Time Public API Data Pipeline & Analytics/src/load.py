import os
import requests
from dotenv import load_dotenv
import pandas as pd
# -------------------------------------------------------------------
# Configuracion
# -------------------------------------------------------------------

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")



headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}


# -------------------------------------------------------------------
# Cargar Datos RAW
# -------------------------------------------------------------------

def cargar_raw(datos_crudos):

    registro = {
        "latitud": datos_crudos["latitude"],
        "longitud": datos_crudos["longitude"],
        "zona_horaria": datos_crudos["timezone"],
        "raw_data": datos_crudos
    }

    endpoint = f"{supabase_url}/rest/v1/weather_raw"

    respuesta = requests.post(
        endpoint,
        headers=headers,
        json=registro,
        timeout=10
    )

    respuesta.raise_for_status()

    return respuesta


# -------------------------------------------------------------------
# Cargar Datos Limpios
# -------------------------------------------------------------------

def cargar_limpios(df):

    if df.empty:
        print("No Hay Registros Para Cargar")
        return

    endpoint = f"{supabase_url}/rest/v1/weather_clean"

    # ---------------------------------------------------------------
    # 1. Obtener las observaciones que ya existen
    # ---------------------------------------------------------------

    parametros_existentes = {
        "select": "latitud,longitud,hora_observacion"
    }

    respuesta_existentes = requests.get(
        endpoint,
        headers=headers,
        params=parametros_existentes,
        timeout=10
    )

    respuesta_existentes.raise_for_status()

    existentes = respuesta_existentes.json()

    # ---------------------------------------------------------------
    # 2. Convertir las observaciones existentes a DataFrame
    # ---------------------------------------------------------------

    df_existentes = pd.DataFrame(
        existentes
    )

    # ---------------------------------------------------------------
    # 3. Comparar las claves de las observaciones
    # ---------------------------------------------------------------

    if not df_existentes.empty:

        df_existentes["hora_observacion"] = pd.to_datetime(
            df_existentes["hora_observacion"],
            errors="coerce"
        )

        df_nuevos = df.merge(
            df_existentes,
            on=[
                "latitud",
                "longitud",
                "hora_observacion"
            ],
            how="left",
            indicator=True
        )

        df_nuevos = df_nuevos[
            df_nuevos["_merge"] == "left_only"
        ]

        df_nuevos = df_nuevos.drop(
            columns=["_merge"]
        )

    else:

        df_nuevos = df.copy()

    # ---------------------------------------------------------------
    # 4. Mostrar resultado incremental
    # ---------------------------------------------------------------

    print(f"Registros recibidos: {len(df)}")
    print(f"Registros ya existentes: {len(df) - len(df_nuevos)}")
    print(f"Registros nuevos: {len(df_nuevos)}")

    if df_nuevos.empty:
        print("No hay registros nuevos para cargar.")
        return

    # ---------------------------------------------------------------
    # 5. Convertir DataFrame a registros
    # ---------------------------------------------------------------

    registros = df_nuevos.to_dict(
        orient="records"
    )

    for registro in registros:

        if registro["hora_observacion"] is not None:

            registro["hora_observacion"] = str(
                registro["hora_observacion"]
            )

    # ---------------------------------------------------------------
    # 6. Insertar solamente los registros nuevos
    # ---------------------------------------------------------------

    headers_insert = {
        **headers,
        "Prefer": "return=minimal"
    }

    respuesta = requests.post(
        endpoint,
        headers=headers_insert,
        json=registros,
        timeout=10
    )

    respuesta.raise_for_status()

    print(
        f"Registros nuevos cargados: {len(registros)}"
    )

    return respuesta

    return respuesta

    return respuesta