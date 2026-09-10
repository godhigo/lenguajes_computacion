from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Dict, List


app = FastAPI(
    title="Evaluador de Autómatas",
    description="Servicio web para evaluar cadenas en AFD y AFN.",
    version="1.0.0",
)

EPSILON_SYMBOLS = {"", "ε", "epsilon", "eps"}


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


@app.get("/")
def inicio():
    return {
        "mensaje": "Evaluador de AFD y AFN",
        "endpoints": {
            "AFD": "POST /afd",
            "AFN": "POST /afn",
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
