from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from itertools import product

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos Pydantic ---

class Lenguaje(BaseModel):
    L: List[str]
    M: List[str]

class LenguajeUnico(BaseModel):
    L: List[str]
    max_len: Optional[int] = 3  # Para limitar la clausura de Kleene

class LenguajeComplemento(BaseModel):
    L: List[str]
    alfabeto: List[str]
    max_len: Optional[int] = 3

class LenguajePotencia(BaseModel):
    L: List[str]
    k: int

# --- Endpoints de Cadenas ---

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/cadenas/concatenar/{x}/{y}")
def concatenar_cadenas(x: str, y: str):
    return {"resultado": x + y}

@app.get("/cadenas/invertir/{x}")
def invertir_cadena(x: str):
    return {"resultado": x[::-1]}

@app.get("/cadenas/potencia/{x}")
def potencia_cadena(x: str, k: int):
    if k <= 0:
        return {"respuesta": ""}
    return {"respuesta": x * k}

# --- Endpoints de Lenguajes ---

@app.post("/lenguajes/union")
def union_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "Union de lenguajes",
        "L": list(L),
        "M": list(M),
        "resultado": list(L.union(M))
    }

@app.post("/lenguajes/interseccion")
def interseccion_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "Interseccion de lenguajes",
        "L": list(L),
        "M": list(M),
        "resultado": list(L.intersection(M))
    }

@app.post("/lenguajes/diferencia")
def diferencia_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "Diferencia de lenguajes",
        "L": list(L),
        "M": list(M),
        "resultado": list(L.difference(M))
    }

@app.post("/lenguajes/concatenacion")
def concatenacion_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    res = {x + y for x in L for y in M}
    return {
        "Operacion": "Concatenacion de lenguajes",
        "L": list(L),
        "M": list(M),
        "resultado": list(res)
    }

@app.post("/lenguajes/potencia")
def potencia_lenguaje(parametro: LenguajePotencia):
    L = set(parametro.L)
    k = parametro.k
    
    if k == 0:
        res = {""}
    else:
        res = set(L)
        for _ in range(k - 1):
            res = {x + y for x in res for y in L}

    return {
        "Operacion": f"Potencia L^{k}",
        "L": list(L),
        "k": k,
        "resultado": list(res)
    }

@app.post("/lenguajes/kleene")
def kleene_lenguaje(parametro: LenguajeUnico):
    L = set(parametro.L)
    max_len = parametro.max_len
    
    # Genera combinaciones desde potencia 0 hasta max_len
    res = {""}
    actual = {""}
    for _ in range(max_len):
        actual = {x + y for x in actual for y in L}
        res.update(actual)
        
    # Ordenar por longitud y alfabéticamente
    res_ordenado = sorted(list(res), key=lambda s: (len(s), s))
    
    return {
        "Operacion": "Clausura de Kleene",
        "L": list(L),
        "resultado": res_ordenado
    }

@app.post("/lenguajes/complemento")
def complemento_lenguaje(parametro: LenguajeComplemento):
    L = set(parametro.L)
    Sigma = parametro.alfabeto
    max_len = parametro.max_len

    universo = {""}
    for i in range(1, max_len + 1):
        for p in product(Sigma, repeat=i):
            universo.add("".join(p))

    res = universo.difference(L)
    res_ordenado = sorted(list(res), key=lambda s: (len(s), s))

    return {
        "Operacion": "Complemento de lenguaje",
        "L": list(L),
        "alfabeto": Sigma,
        "resultado": res_ordenado
    }