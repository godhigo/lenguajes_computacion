# Simulación meteorológica paralela (Ghost Cells + Pipes)

| Dato | Información |
|---|---|
| Nombre de la actividad | Simulación meteorológica paralela |
| Alumno | **Diego Navarro Sánchez** |
| No. de cuenta | **202497** |
| Materia | **Lenguajes de Computación** |
| Profesor(a) | **Paulo Vázquez** |

Práctica de simulación meteorológica en una malla N × N, paralelizada por descomposición en
franjas horizontales con intercambio de *ghost cells* entre procesos vecinos mediante
`multiprocessing.Pipe`.

| Archivo | Descripción |
|---|---|
| `practica_simulacion_meteorologica.ipynb` | Cuaderno principal: código base corregido (Fases 1–4), orquestación (Fase 5), tabla de evaluación para P = 1, 2, 4, 8, experimentos y respuestas |
| `sim_meteo.py` | Módulo con las funciones de la simulación (el cuaderno lo genera con `%%writefile`) |

## Ejecución

```bash
pip install numpy pandas matplotlib jinja2 notebook
jupyter notebook practica_simulacion_meteorologica.ipynb    # Run → Run All Cells
```

También funciona en Google Colab (*Entorno de ejecución → Ejecutar todas*). Tarda unos
5 minutos. Para que P = 4 y P = 8 sean representativos, conviene un equipo con ≥ 8 núcleos.
