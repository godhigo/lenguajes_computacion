"""Gráficas opcionales a partir del CSV. Requiere matplotlib.

Instalación opcional: python3 -m pip install matplotlib
Uso: python3 graficas.py
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path


def main():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("Instala matplotlib para generar las gráficas: python3 -m pip install matplotlib") from exc

    carpeta = Path(__file__).resolve().parent / "resultados"
    with (carpeta / "mediciones.csv").open(newline="", encoding="utf-8") as f:
        datos = list(csv.DictReader(f))

    medidas = (
        ("tiempo_ms", "Tiempo promedio de multiplicación (ms)", "tiempo.png"),
        ("memoria_pico_kib", "Pico de memoria rastreada (KiB)", "memoria.png"),
        ("multiplicaciones_digito", "Multiplicaciones elementales de dígitos", "operaciones.png"),
    )
    agrupado = defaultdict(list)
    for fila in datos:
        agrupado[(fila["variante"], int(fila["digitos"]))].append(fila)
    variantes = list(dict.fromkeys(f["variante"] for f in datos))
    tamanos = sorted({int(f["digitos"]) for f in datos})

    for campo, titulo, archivo in medidas:
        fig, ax = plt.subplots(figsize=(9, 5))
        for variante in variantes:
            xs = tamanos
            ys = [statistics.mean(float(f[campo]) for f in agrupado[(variante, n)])
                  for n in tamanos]
            ax.plot(xs, ys, marker="o", label=variante)
        ax.set_title(f"Actividad 14 — {titulo}")
        ax.set_xlabel("Número de dígitos por operando (N)")
        ax.set_ylabel(titulo)
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(carpeta / archivo, dpi=160)
        plt.close(fig)
        print("Creada:", carpeta / archivo)


if __name__ == "__main__":
    main()
