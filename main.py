from pathlib import Path
import re
from typing import Dict, List

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, field_validator


app = FastAPI(
    title="Evaluador de Autómatas y Analizador de Complejidad",
    description=(
        "Servicio web para evaluar cadenas en AFD y AFN, y analizar "
        "complejidad algorítmica de archivos de código fuente."
    ),
    version="2.0.0",
)

EPSILON_SYMBOLS = {"", "ε", "epsilon", "eps"}
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
MAX_SOURCE_FILE_SIZE = 1_000_000  # 1 MB


class AFDRequest(BaseModel):
    tabla_transicion: Dict[str, Dict[str, str]]
    cadenas: List[str]
    estado_inicial: str
    estados_finales: List[str]

    @field_validator("cadenas")
    @classmethod
    def validar_cadenas(cls, cadenas):
        if not cadenas:
            raise ValueError("Debe enviarse al menos una cadena.")
        return cadenas


class AFNRequest(BaseModel):
    tabla_transicion: Dict[str, Dict[str, List[str]]]
    cadenas: List[str]
    estado_inicial: str
    estados_finales: List[str]

    @field_validator("cadenas")
    @classmethod
    def validar_cadenas(cls, cadenas):
        if not cadenas:
            raise ValueError("Debe enviarse al menos una cadena.")
        return cadenas


def es_epsilon(simbolo: str) -> bool:
    return simbolo in EPSILON_SYMBOLS


def obtener_datos_afd(data: AFDRequest):
    estados = {data.estado_inicial, *data.estados_finales}
    alfabeto = set()

    for origen, transiciones in data.tabla_transicion.items():
        estados.add(origen)

        for simbolo, destino in transiciones.items():
            if es_epsilon(simbolo):
                raise HTTPException(
                    status_code=400,
                    detail="Un AFD no puede contener transiciones epsilon."
                )

            if len(simbolo) != 1:
                raise HTTPException(
                    status_code=400,
                    detail=f"El símbolo '{simbolo}' debe tener un solo carácter."
                )

            alfabeto.add(simbolo)
            estados.add(destino)

    return sorted(estados), sorted(alfabeto)


def obtener_datos_afn(data: AFNRequest):
    estados = {data.estado_inicial, *data.estados_finales}
    alfabeto = set()

    for origen, transiciones in data.tabla_transicion.items():
        estados.add(origen)

        for simbolo, destinos in transiciones.items():
            if not es_epsilon(simbolo):
                if len(simbolo) != 1:
                    raise HTTPException(
                        status_code=400,
                        detail=f"El símbolo '{simbolo}' debe tener un solo carácter."
                    )
                alfabeto.add(simbolo)

            estados.update(destinos)

    return sorted(estados), sorted(alfabeto)


def epsilon_closure(
    estados: set[str],
    tabla: Dict[str, Dict[str, List[str]]]
) -> set[str]:
    cierre = set(estados)
    pendientes = list(estados)

    while pendientes:
        estado = pendientes.pop()

        for simbolo in EPSILON_SYMBOLS:
            for destino in tabla.get(estado, {}).get(simbolo, []):
                if destino not in cierre:
                    cierre.add(destino)
                    pendientes.append(destino)

    return cierre


def generar_respuesta_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Envía un prompt a Ollama y devuelve únicamente el texto generado."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "No fue posible comunicarse con Ollama. Verifica que "
                "'ollama serve' esté ejecutándose y que el modelo "
                f"'{OLLAMA_MODEL}' esté instalado. Detalle: {exc}"
            ),
        ) from exc

    try:
        data = response.json()
        generated = data["response"]
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Ollama devolvió una respuesta con un formato inesperado.",
        ) from exc

    if not generated.strip():
        raise HTTPException(
            status_code=502,
            detail="Ollama devolvió una respuesta vacía.",
        )

    return generated


def limpiar_respuesta_modelo(respuesta: str) -> str:
    """Elimina un bloque Markdown accidental sin modificar el código interno."""
    respuesta = respuesta.strip()
    bloque = re.search(r"```[^\n]*\n(.*?)```", respuesta, flags=re.DOTALL)
    if bloque:
        return bloque.group(1).strip()
    return respuesta


def construir_prompt_complejidad(
    codigo: str,
    nombre_archivo: str,
    notacion: str,
    escenario: str,
) -> str:
    return f"""
Eres un experto en análisis de complejidad algorítmica y lenguajes de programación.
Analiza el archivo '{nombre_archivo}' en el escenario de {escenario} usando notación {notacion}.

REGLAS OBLIGATORIAS:
1. Devuelve ÚNICAMENTE el contenido completo del archivo fuente anotado. No uses Markdown, no uses triple acento grave y no agregues explicaciones fuera del archivo.
2. Conserva el código original, su orden y su comportamiento. No reescribas ni optimices el programa.
3. Agrega comentarios de complejidad línea por línea. Usa la sintaxis de comentarios propia del lenguaje del archivo.
4. Para líneas vacías o que solo contienen llaves/cierres, puedes omitir el comentario si no representan una operación; para las demás líneas explica brevemente el costo y escribe su notación {notacion}.
5. Si un comentario al final de una línea pudiera romper la sintaxis, colócalo inmediatamente antes de esa línea.
6. Evalúa ciclos, ciclos anidados, llamadas, recursión, condicionales, acceso a estructuras, ordenamientos, búsquedas y operaciones de entrada/salida según corresponda.
7. Al FINAL del archivo agrega un bloque de comentarios llamado "RESUMEN DE COMPLEJIDAD - {notacion}" que incluya exactamente estos conceptos:
   - "Suma de complejidades individuales:" seguido por una expresión que muestre la suma de los costos identificados y su simplificación asintótica.
   - "Complejidad de mayor grado:" seguido por la complejidad dominante encontrada.
   - Una explicación breve de por qué ese término domina.
8. En {notacion}, analiza el {escenario}; no mezcles el resultado con otra notación asintótica.

ARCHIVO ORIGINAL:
{codigo}
""".strip()


async def analizar_archivo_complejidad(
    archivo: UploadFile,
    notacion: str,
    escenario: str,
    sufijo: str,
) -> Response:
    if not archivo.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener un nombre.",
        )

    contenido = await archivo.read()

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo enviado está vacío.",
        )

    if len(contenido) > MAX_SOURCE_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="El archivo supera el límite de 1 MB.",
        )

    try:
        codigo = contenido.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser texto codificado en UTF-8.",
        ) from exc

    nombre_seguro = Path(archivo.filename).name
    prompt = construir_prompt_complejidad(
        codigo=codigo,
        nombre_archivo=nombre_seguro,
        notacion=notacion,
        escenario=escenario,
    )

    resultado = generar_respuesta_ollama(prompt)
    resultado = limpiar_respuesta_modelo(resultado)

    ruta = Path(nombre_seguro)
    nombre_salida = f"{ruta.stem}_{sufijo}{ruta.suffix}"

    return Response(
        content=resultado,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre_salida}"',
            "X-Complexity-Notation": "Big-Omega" if "Omega" in notacion else "Big-O",
        },
    )


@app.get("/")
def inicio():
    return {
        "mensaje": "Evaluador de AFD y AFN",
        "endpoints": {
            "AFD": "POST /afd",
            "AFN": "POST /afn",
            "Big-O (peor caso)": "POST /complejidad/big-o",
            "Big-Omega (mejor caso)": "POST /complejidad/big-omega",
            "documentacion": "/docs"
        }
    }


@app.post("/afd")
def evaluar_afd(data: AFDRequest):
    estados, alfabeto = obtener_datos_afd(data)
    finales = set(data.estados_finales)
    resultados = []

    for cadena in data.cadenas:
        estado_actual = data.estado_inicial
        transiciones = []
        error = None

        for simbolo in cadena:
            if simbolo not in alfabeto:
                transiciones.append(
                    f"δ({estado_actual}, {simbolo}) = ∅"
                )
                error = f"El símbolo '{simbolo}' no pertenece al alfabeto."
                estado_actual = None
                break

            destino = data.tabla_transicion.get(estado_actual, {}).get(simbolo)

            if destino is None:
                transiciones.append(
                    f"δ({estado_actual}, {simbolo}) = ∅"
                )
                error = (
                    f"No existe transición desde el estado "
                    f"'{estado_actual}' con el símbolo '{simbolo}'."
                )
                estado_actual = None
                break

            transiciones.append(
                f"δ({estado_actual}, {simbolo}) = {destino}"
            )
            estado_actual = destino

        aceptada = estado_actual in finales if estado_actual is not None else False

        resultados.append({
            "cadena": cadena,
            "aceptada": aceptada,
            "resultado": "ACEPTADA" if aceptada else "RECHAZADA",
            "estado_al_terminar": estado_actual,
            "transiciones": transiciones,
            "error": error
        })

    return {
        "tipo": "AFD",
        "estados_totales": estados,
        "cantidad_estados": len(estados),
        "alfabeto": alfabeto,
        "estado_inicial": data.estado_inicial,
        "estados_finales": sorted(data.estados_finales),
        "resultados": resultados
    }


@app.post("/afn")
def evaluar_afn(data: AFNRequest):
    estados, alfabeto = obtener_datos_afn(data)
    finales = set(data.estados_finales)
    resultados = []

    for cadena in data.cadenas:
        estados_actuales = epsilon_closure(
            {data.estado_inicial},
            data.tabla_transicion
        )

        transiciones = [
            (
                f"ε-cierre({{{data.estado_inicial}}}) = "
                f"{{{', '.join(sorted(estados_actuales))}}}"
            )
        ]

        error = None

        for simbolo in cadena:
            if simbolo not in alfabeto:
                transiciones.append(
                    f"δ({{{', '.join(sorted(estados_actuales))}}}, {simbolo}) = ∅"
                )
                estados_actuales = set()
                error = f"El símbolo '{simbolo}' no pertenece al alfabeto."
                break

            antes = set(estados_actuales)
            destinos = set()

            for estado in antes:
                destinos.update(
                    data.tabla_transicion.get(estado, {}).get(simbolo, [])
                )

            transiciones.append(
                (
                    f"δ({{{', '.join(sorted(antes))}}}, {simbolo}) = "
                    f"{{{', '.join(sorted(destinos))}}}"
                )
            )

            estados_actuales = epsilon_closure(
                destinos,
                data.tabla_transicion
            )

            transiciones.append(
                (
                    f"ε-cierre({{{', '.join(sorted(destinos))}}}) = "
                    f"{{{', '.join(sorted(estados_actuales))}}}"
                )
            )

        aceptada = bool(estados_actuales & finales)

        resultados.append({
            "cadena": cadena,
            "aceptada": aceptada,
            "resultado": "ACEPTADA" if aceptada else "RECHAZADA",
            "estados_al_terminar": sorted(estados_actuales),
            "transiciones": transiciones,
            "error": error
        })

    return {
        "tipo": "AFN",
        "estados_totales": estados,
        "cantidad_estados": len(estados),
        "alfabeto": alfabeto,
        "estado_inicial": data.estado_inicial,
        "estados_finales": sorted(data.estados_finales),
        "resultados": resultados
    }


@app.post(
    "/complejidad/big-o",
    summary="Analizar complejidad en el peor caso (Big-O)",
    response_class=Response,
)
async def analizar_big_o(
    archivo: UploadFile = File(..., description="Archivo de código fuente en UTF-8"),
):
    return await analizar_archivo_complejidad(
        archivo=archivo,
        notacion="Big-O",
        escenario="peor caso",
        sufijo="big_o",
    )


@app.post(
    "/complejidad/big-omega",
    summary="Analizar complejidad en el mejor caso (Big-Omega)",
    response_class=Response,
)
async def analizar_big_omega(
    archivo: UploadFile = File(..., description="Archivo de código fuente en UTF-8"),
):
    return await analizar_archivo_complejidad(
        archivo=archivo,
        notacion="Big-Omega (Ω)",
        escenario="mejor caso",
        sufijo="big_omega",
    )

