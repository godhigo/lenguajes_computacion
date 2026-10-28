"""Experimento reproducible para T(N) y S(N): tiempos, memoria y operaciones.

Uso:
    python3 benchmark.py
    python3 benchmark.py --repeticiones 7 --casos 5

Sin librerías externas. Las gráficas son opcionales (ver graficas.py).
"""

from __future__ import annotations

import argparse
import csv
import platform
import random
import statistics
import time
import tracemalloc
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from karatsuba import Estadisticas, multiplicar

TAMANOS = (20, 50, 100)
VARIANTES = (
    ("escuela", 1, "Escuela"),
    ("divide4", 1, "Divide4"),
    ("karatsuba", 1, "Karatsuba u=1"),
    ("karatsuba", 8, "Karatsuba u=8"),
    ("karatsuba", 16, "Karatsuba u=16"),
)
CAMPOS = ["digitos", "caso", "variante", "metodo", "umbral", "tiempo_ms",
          "memoria_pico_kib", "multiplicaciones_digito", "llamadas",
          "casos_base", "profundidad_maxima", "correcto"]


def crear_numero(azar: random.Random, n: int) -> str:
    return str(azar.randrange(1, 10)) + "".join(
        str(azar.randrange(10)) for _ in range(n - 1)
    )


def medir(a: str, b: str, metodo: str, umbral: int,
          repeticiones: int, esperado: str) -> dict:
    """Mide tiempo sin tracemalloc; memoria en ejecución independiente."""
    duraciones = []
    for _ in range(repeticiones):
        inicio = time.perf_counter_ns()
        resultado = multiplicar(a, b, metodo=metodo, umbral=umbral)
        duraciones.append((time.perf_counter_ns() - inicio) / 1_000_000)
        if resultado != esperado:
            raise AssertionError(f"Error de multiplicación con {metodo}, umbral {umbral}")

    tracemalloc.start()
    try:
        metricas = Estadisticas()
        resultado = multiplicar(a, b, metodo=metodo,
                               umbral=umbral, datos=metricas)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if resultado != esperado:
        raise AssertionError("Resultado incorrecto durante el muestreo de memoria")

    return {
        "tiempo_ms": round(statistics.median(duraciones), 5),
        "memoria_pico_kib": round(pico / 1024, 3),
        "multiplicaciones_digito": metricas.multiplicaciones_digito,
        "llamadas": metricas.llamadas,
        "casos_base": metricas.casos_base,
        "profundidad_maxima": metricas.profundidad_maxima,
        "correcto": "SI",
    }


def producir_informe(filas: list[dict], casos: int,
                     repeticiones: int) -> str:
    grupos = defaultdict(list)
    for fila in filas:
        grupos[(fila["digitos"], fila["variante"])].append(fila)

    lineas = [
        "# Resultados experimentales: Actividad 14",
        "",
        f"Ejecutado (UTC): **{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}**.  ",
        f"Python: **{platform.python_version()}**. Sistema: **{platform.system()} {platform.machine()}**.  ",
        f"Datos: **{casos} pares pseudoaleatorios por tamaño**, semilla fija 2026.  ",
        f"Tiempos: **mediana de {repeticiones} ejecuciones por par**; la tabla presenta el promedio de esas medianas.",
        "",
        "## T(N): tiempo y cantidad de operaciones",
        "",
        "| Dígitos por operando | Variante | Tiempo medio (ms) | Productos de dígitos (prom.) | Llamadas (prom.) | Prof. máx. (prom.) |",
        "| ---: | :--- | ---: | ---: | ---: | ---: |",
    ]
    for n in TAMANOS:
        for _, _, etiqueta in VARIANTES:
            grupo = grupos[(n, etiqueta)]
            def prom(campo):
                return statistics.mean(f[campo] for f in grupo)
            lineas.append(f"| {n} | {etiqueta} | {prom('tiempo_ms'):.4f} | "
                          f"{prom('multiplicaciones_digito'):.1f} | "
                          f"{prom('llamadas'):.1f} | {prom('profundidad_maxima'):.1f} |")

    lineas += [
        "",
        "## S(N): memoria adicional observada",
        "",
        "| Dígitos por operando | Variante | Pico medio (KiB) |",
        "| ---: | :--- | ---: |",
    ]
    for n in TAMANOS:
        for _, _, etiqueta in VARIANTES:
            grupo = grupos[(n, etiqueta)]
            prom = statistics.mean(f["memoria_pico_kib"] for f in grupo)
            lineas.append(f"| {n} | {etiqueta} | {prom:.3f} |")
    lineas += [
        "",
        "## Interpretación",
        "",
        "- **Escuela** realiza n² multiplicaciones de dígitos cuando los dos números tienen n dígitos.",
        "- **Divide4** utiliza cuatro subproblemas: T(n)=4T(n/2)+O(n), del orden O(n²).",
        "- **Karatsuba** utiliza tres: T(n)=3T(n/2)+O(n), del orden O(n^1.585).",
        "- Un umbral 8 o 16 aplica la multiplicación tradicional en subproblemas pequeños; "
        "la recurrencia superior sigue siendo la de Karatsuba.",
        "- **S(n)** teórica de las versiones recursivas, incluyendo temporales, es O(n), "
        "con profundidad de pila O(log n); la implementación escolar usa O(n) para el resultado.",
        "- `tracemalloc` mide **memoria rastreada por Python durante esa operación**, no "
        "la RAM total del proceso. Sus cifras dependen del intérprete y las condiciones de ejecución.",
        "- El tiempo real puede favorecer a Escuela para tamaños pequeños debido al costo "
        "de la recursión y de manipular cadenas en Python, aunque Karatsuba reduzca productos de dígitos.",
        "- Todas las operaciones fueron verificadas frente a `int(a) * int(b)` "
        "**sólo como referencia**; las implementaciones analizadas no usan ese producto nativo.",
        "",
        "Para repetir: `python3 benchmark.py --casos 3 --repeticiones 5`.",
        "Los datos por caso están en `mediciones.csv` y los operandos/productos en `casos.csv`.",
    ]
    return "\n".join(lineas) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mediciones reproducibles T(N) y S(N)")
    parser.add_argument("--casos", type=int, default=3,
                        help="Pares de números por tamaño (predeterminado: 3)")
    parser.add_argument("--repeticiones", type=int, default=5,
                        help="Repeticiones por caso para tiempo (predeterminado: 5)")
    parser.add_argument("--directorio", type=Path,
                        default=Path(__file__).resolve().parent / "resultados")
    args = parser.parse_args()
    if args.casos < 1 or args.repeticiones < 1:
        parser.error("--casos y --repeticiones deben ser >= 1")
    args.directorio.mkdir(parents=True, exist_ok=True)

    generador = random.Random(2026)
    filas = []
    operandos = []
    for n in TAMANOS:
        for indice in range(1, args.casos + 1):
            a, b = crear_numero(generador, n), crear_numero(generador, n)
            esperado = str(int(a) * int(b))  # Referencia; nunca la solución.
            operandos.append({"digitos": n, "caso": indice,
                              "a": a, "b": b, "producto": esperado})
            for metodo, umbral, etiqueta in VARIANTES:
                medidas = medir(a, b, metodo, umbral, args.repeticiones, esperado)
                filas.append({"digitos": n, "caso": indice,
                              "variante": etiqueta, "metodo": metodo,
                              "umbral": umbral, **medidas})
                print(f"{n:3d} dígitos | caso {indice:2d} | {etiqueta:15s} | "
                      f"{medidas['tiempo_ms']:.3f} ms | "
                      f"{medidas['multiplicaciones_digito']} productos")

    with (args.directorio / "mediciones.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)
    with (args.directorio / "casos.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["digitos", "caso", "a", "b", "producto"])
        escritor.writeheader()
        escritor.writerows(operandos)
    informe = producir_informe(filas, args.casos, args.repeticiones)
    (args.directorio / "INFORME.md").write_text(informe, encoding="utf-8")
    print("\nArchivos generados en", args.directorio)


if __name__ == "__main__":
    main()
