# Actividad 15. Implementación de técnicas de Programación Dinámica

| Dato | Información |
|---|---|
| Nombre de la actividad | Problema del corte de varillas (Rod Cutting) |
| Alumno | **Diego Navarro Sánchez** |
| No. de cuenta | **202497** |
| Materia | **Lenguajes de Computación** |
| Profesor(a) | **Paulo Vázquez** |

Implementación del problema del corte de varillas con tres técnicas y su comparación:

1. **Recursiva pura**: O(2ⁿ).
2. **Memoización (Top-Down)**: recursión con caché, O(n²).
3. **Tabulación (Bottom-Up)**: llenado iterativo de la tabla, O(n²).

Las tres funciones están adaptadas para devolver, además del ingreso máximo, **los cortes**
que lo producen.

| Archivo | Descripción |
|---|---|
| `programacion_dinamica.ipynb` | Libreta del profesor completada: tabulación, versiones con cortes, verificación, benchmark, tabla, gráfica y análisis |
| `benchmark_corte_varillas.csv` | Tiempos medidos (ms) para n = 5, 10, 15, 20, 25, 28 y 30 |
| `benchmark_corte_varillas.png` | Gráfica de tiempo vs. longitud de la varilla |

## Ejecución

```bash
pip install pandas matplotlib jupyter
jupyter notebook programacion_dinamica.ipynb      # Run → Run All Cells
```

La celda del benchmark tarda unos 5 minutos por la versión recursiva con n = 28 y n = 30.
