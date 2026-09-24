import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def extraer_clima(latitude, longitude):

    api = "https://api.open-meteo.com/v1/forecast"

    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "pressure_msl,"
            "surface_pressure,"
            "cloud_cover,"
            "visibility,"
            "wind_speed_10m,"
            "wind_gusts_10m,"
            "temperature_80m,"
            "precipitation_probability"
        ),
        "timezone": "auto"
    }

    reintentos = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    session = requests.Session()

    adaptador = HTTPAdapter(
        max_retries=reintentos
    )

    session.mount(
        "https://",
        adaptador
    )

    respuesta = session.get(
        api,
        params=parametros,
        timeout=10
    )

    respuesta.raise_for_status()

    datos_crudos = respuesta.json()

    return datos_crudos