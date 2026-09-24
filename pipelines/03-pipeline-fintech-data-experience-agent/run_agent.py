
import json
import os
import sys
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

from src.ai_agent.database_tool import get_customer_profile


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] No se encontró GEMINI_API_KEY.")
    print("Configura la variable en el archivo .env.")
    sys.exit(1)


API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.6-flash:generateContent"
)

HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": api_key
}


# ============================================================
# INSTRUCCIONES DEL AGENTE
# ============================================================

SYSTEM_INSTRUCTION = """
Eres un agente de Customer Experience para MACHBANK.

Tu función es ayudar al equipo de operaciones a analizar
información sintética de clientes de una billetera digital.

Cuando el usuario solicite información sobre un cliente,
utiliza la herramienta get_customer_profile.

Con los datos obtenidos, entrega un análisis estructurado:

1. Perfil del cliente.
2. Métricas y comportamiento.
3. Segmento asignado.
4. Observaciones de negocio.
5. Recomendación orientada a fidelización o experiencia
   del cliente.

No inventes datos que no estén disponibles en la herramienta.

No tomes decisiones financieras ni otorgues aprobaciones.

Las recomendaciones deben considerarse como apoyo para
el análisis y no como decisiones automatizadas.
"""


# ============================================================
# DEFINICIÓN DE LA HERRAMIENTA
# ============================================================

TOOL_DECLARATION = {
    "function_declarations": [
        {
            "name": "get_customer_profile",
            "description": (
                "Obtiene el perfil consolidado de un cliente "
                "desde la base analítica SQLite."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "customer_id": {
                        "type": "STRING",
                        "description": (
                            "Identificador único del cliente. "
                            "Ejemplo: cust_0000"
                        )
                    }
                },
                "required": ["customer_id"]
            }
        }
    ]
}


# ============================================================
# LLAMADA A GEMINI
# ============================================================

def enviar_a_gemini(contents: list, reintentos: int = 3) -> dict:
    """
    Envía la conversación a Gemini.

    Reintenta automáticamente ante errores temporales
    HTTP 429 o 503.
    """

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },
        "contents": contents,
        "tools": [
            TOOL_DECLARATION
        ],
        "generationConfig": {
            "temperature": 0.2
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=HEADERS,
        method="POST"
    )

    for intento in range(reintentos):

        try:

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:

            if error.code in (429, 503):

                if intento < reintentos - 1:

                    espera = 2 ** intento

                    print(
                        f"[AVISO] Gemini respondió HTTP "
                        f"{error.code}. "
                        f"Reintentando en {espera} segundos..."
                    )

                    time.sleep(espera)
                    continue

                print(
                    f"[ERROR] Gemini respondió HTTP "
                    f"{error.code} después de "
                    f"{reintentos} intentos."
                )

                raise RuntimeError(
                    f"Gemini no está disponible temporalmente "
                    f"(HTTP {error.code})."
                ) from error

            detalle = error.read().decode(
                "utf-8",
                errors="replace"
            )

            print(
                f"[ERROR] Gemini respondió con HTTP "
                f"{error.code}."
            )

            print(detalle)

            raise

        except urllib.error.URLError as error:

            print(
                f"[ERROR] No fue posible conectarse con Gemini: "
                f"{error}"
            )

            raise

        except TimeoutError:

            if intento < reintentos - 1:

                espera = 2 ** intento

                print(
                    "[AVISO] La solicitud a Gemini superó "
                    f"el tiempo de espera. "
                    f"Reintentando en {espera} segundos..."
                )

                time.sleep(espera)
                continue

            print(
                "[ERROR] Gemini no respondió dentro "
                "del tiempo establecido."
            )

            raise

    raise RuntimeError(
        "No fue posible obtener una respuesta de Gemini."
    )


# ============================================================
# EXTRACCIÓN DE CONTENIDO
# ============================================================

def extraer_contenido(respuesta: dict) -> dict:
    """
    Obtiene el contenido generado por Gemini.
    """

    candidatos = respuesta.get("candidates", [])

    if not candidatos:
        raise RuntimeError(
            "Gemini no devolvió candidatos en la respuesta."
        )

    contenido = candidatos[0].get("content")

    if not contenido:
        raise RuntimeError(
            "Gemini no devolvió contenido válido."
        )

    return contenido


# ============================================================
# EJECUCIÓN DEL AGENTE
# ============================================================

def consultar_agente(pregunta: str) -> str:
    """
    Ejecuta una consulta utilizando Gemini y la herramienta
    get_customer_profile.
    """

    print(f"\n[Usuario]: {pregunta}")

    print(
        "[Agente]: Analizando la consulta y verificando "
        "la base analítica...\n"
    )

    conversacion = [
        {
            "role": "user",
            "parts": [
                {
                    "text": pregunta
                }
            ]
        }
    ]

    # --------------------------------------------------------
    # PRIMERA LLAMADA: Gemini decide si necesita la herramienta
    # --------------------------------------------------------

    resultado_1 = enviar_a_gemini(conversacion)

    candidato_1 = extraer_contenido(resultado_1)

    # Conservamos la respuesta completa del modelo.
    conversacion.append(candidato_1)

    llamada_funcion = None

    for part in candidato_1.get("parts", []):

        if "functionCall" in part:

            llamada_funcion = part["functionCall"]
            break

    # --------------------------------------------------------
    # Si Gemini no solicita herramienta
    # --------------------------------------------------------

    if not llamada_funcion:

        for part in candidato_1.get("parts", []):

            if "text" in part:
                return part["text"]

        return "No se pudo completar el análisis."

    # --------------------------------------------------------
    # DATOS DEL FUNCTION CALL
    # --------------------------------------------------------

    nombre_funcion = llamada_funcion.get("name")

    argumentos = llamada_funcion.get(
        "args",
        {}
    )

    if nombre_funcion != "get_customer_profile":

        return (
            f"La herramienta solicitada no está disponible: "
            f"{nombre_funcion}"
        )

    customer_id = argumentos.get(
        "customer_id"
    )

    if not customer_id:

        return (
            "No fue posible identificar el Customer_ID "
            "solicitado."
        )

    print(
        "[Tool Execution] Consultando SQLite para "
        f"customer_id='{customer_id}'..."
    )

    # --------------------------------------------------------
    # EJECUCIÓN DE LA HERRAMIENTA
    # --------------------------------------------------------

    datos_cliente = get_customer_profile(
        customer_id
    )

    # --------------------------------------------------------
    # RESPUESTA DE LA HERRAMIENTA
    # --------------------------------------------------------

    conversacion.append(
        {
            "role": "user",
            "parts": [
                {
                    "functionResponse": {
                        "name": nombre_funcion,
                        "response": {
                            "result": datos_cliente
                        }
                    }
                }
            ]
        }
    )

    # --------------------------------------------------------
    # SEGUNDA LLAMADA: Gemini genera el diagnóstico
    # --------------------------------------------------------

    resultado_2 = enviar_a_gemini(
        conversacion
    )

    candidato_2 = extraer_contenido(
        resultado_2
    )

    for part in candidato_2.get("parts", []):

        if "text" in part:

            return part["text"]

    return (
        "La herramienta fue ejecutada correctamente, "
        "pero no se obtuvo un diagnóstico textual."
    )


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":

    pregunta_prueba = (
        "Necesito revisar el perfil de 'cust_0000' "
        "para analizar su comportamiento y determinar "
        "si podría ser considerado para una campaña "
        "especial de fidelización."
    )

    try:
        resultado = consultar_agente(
            pregunta_prueba
        )

        print("\n" + "=" * 70)
        print("DIAGNÓSTICO DEL AGENTE")
        print("=" * 70)
        print(resultado)
        print("=" * 70)

    except RuntimeError as error:
        print("\n" + "=" * 70)
        print("AGENTE NO DISPONIBLE")
        print("=" * 70)
        print(f"[ERROR] {error}")
        print("=" * 70)