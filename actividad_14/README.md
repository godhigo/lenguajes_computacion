# Actividad 14 — Implementación de Divide y Vencerás (Karatsuba)

**Objetivo:** implementar recursivamente el algoritmo Karatsuba para multiplicar enteros grandes de **20, 50 y 100 dígitos**, analizar **T(N)** (tiempo) y **S(N)** (espacio), y comparar resultados contra el método tradicional sin Karatsuba.

**Lenguaje:** Python 3.10 o superior. El programa principal **no utiliza `int(a) * int(b)` para multiplicar números grandes**: las cantidades se procesan como cadenas decimales, y sólo se multiplica directamente un dígito por otro (0–9). La multiplicación nativa de Python aparece exclusivamente en las pruebas y el benchmark como referencia para comprobar la respuesta.

## Archivos del proyecto

```text
actividad14-karatsuba/
├── karatsuba.py             # Escuela, Divide4 y Karatsuba recursivos
├── benchmark.py             # Medición de T(N), S(N) y conteo de operaciones
├── graficas.py              # Generador opcional de gráficas (matplotlib)
├── tests/
│   └── test_karatsuba.py    # Pruebas automáticas
├── resultados/
│   ├── casos.csv            # Operand(os) exactos y productos esperados
│   ├── mediciones.csv       # Experimentos para cada tamaño y variante
│   ├── INFORME.md           # Tablas, mediciones y análisis
│   ├── tiempo.png
│   ├── memoria.png
│   └── operaciones.png
├── .gitignore
└── README.md
```

## 1. La estrategia Divide y Vencerás

Para multiplicar dos números grandes `x` e `y`, tomamos `m = floor(N / 2)` y separamos sus partes alta y baja:

```text
x = a · 10^m + b
y = c · 10^m + d
```

**Fase 1 — División.** Separamos los dos operandos en `a, b, c, d` (sin convertir el entero completo a un tipo de tamaño limitado). Si el número de dígitos es impar, las partes pueden tener tamaños diferentes.

**Fase 2 — Conquista.** La expansión tradicional requiere cuatro productos: `ac`, `ad`, `bc`, `bd`. Karatsuba reduce este trabajo a **tres multiplicaciones recursivas**:

```text
z2 = Karatsuba(a, c)
z0 = Karatsuba(b, d)
p  = Karatsuba(a + b, c + d)
z1 = p - z2 - z0       # equivale a ad + bc
```

**Fase 3 — Integración.** Combinamos los resultados parciales usando sumas y desplazamientos decimales:

```text
resultado = z2 · 10^(2m) + z1 · 10^m + z0
```

En `karatsuba.py` los desplazamientos por potencias de 10 **se realizan agregando ceros a cadenas** (no mediante una multiplicación nativa sobre enteros grandes). Para casos base de hasta `umbral` dígitos se usa la multiplicación escolar.

### Ejemplo manual: 1234 × 5678

```text
m = 2,  a=12, b=34, c=56, d=78
z2 = 12 × 56 = 672
z0 = 34 × 78 = 2652
p  = (12+34) × (56+78) = 46 × 134 = 6164
z1 = 6164 - 672 - 2652 = 2840

resultado = 672 × 10000 + 2840 × 100 + 2652 = 7006652
```

En el ejemplo anterior se muestran productos numéricos para explicar la fórmula; el programa calcula esos productos recursivamente.

## 2. Variantes que se comparan

| Variante | Subproductos por división | Caso base | Complejidad temporal |
| --- | ---: | --- | --- |
| `escuela` | No aplica | Multiplicación por columnas | O(N²) |
| `divide4` | 4 | Escuela con umbral=1 | O(N²) |
| `karatsuba`, umbral=1 | 3 | Escuela para 1 dígito | O(N^log₂3) ≈ O(N^1.585) |
| `karatsuba`, umbral=8 | 3 | Escuela hasta 8 dígitos | O(N^1.585) |
| `karatsuba`, umbral=16 | 3 | Escuela hasta 16 dígitos | O(N^1.585) |

Los umbrales no cambian la complejidad asintótica: pueden ahorrar llamadas recursivas para entradas pequeñas. En las pruebas, la multiplicación escolar representa la comparación **sin Karatsuba**; además, `divide4` muestra qué sucede si dividimos el problema de manera recursiva **sin la mejora de tres productos**.

## 3. Análisis de T(N) y S(N)

Para operandos de tamaños comparables:

- **Escuela:** `T(N) = O(N²)` por recorrer todos los pares de dígitos.
- **Divide4:** `T(N) = 4T(N/2) + O(N) = O(N²)`.
- **Karatsuba:** `T(N) = 3T(N/2) + O(N) = O(N^log₂3)`.
- **Karatsuba híbrido:** utiliza `T(N) = O(N²)` como caso base para `N ≤ umbral`, pero conserva `O(N^log₂3)` globalmente con umbral constante.
- **Espacio auxiliar:** multiplicación escolar `S(N)=O(N)` por su arreglo de resultado. Las versiones recursivas requieren `S(N)=S(N/2)+O(N)=O(N)` considerando cadenas temporales, más `O(log N)` marcos de recursión anidados (incluidos en la cota lineal de memoria total).

**Cómo se mide:** `benchmark.py` genera tres parejas pseudoaleatorias de **20, 50 y 100 dígitos cada una** (semilla fija `2026`), realiza cinco mediciones de tiempo con `time.perf_counter_ns()` para cada par y variante, y guarda la mediana. Mide por separado la memoria pico de las asignaciones rastreadas por Python usando `tracemalloc`. También cuenta las multiplicaciones elementales, las llamadas recursivas y la profundidad máxima. El archivo `resultados/INFORME.md` presenta los promedios por tamaño y método; `resultados/mediciones.csv` conserva los datos individuales.

**Limitaciones:** los tiempos dependen del equipo y de la carga del sistema; `tracemalloc` no equivale a la RAM del sistema. Para N de 20–100, la versión escolar puede tardar menos que Karatsuba a pesar de efectuar más multiplicaciones elementales, debido al costo de la recursión en Python.

## 4. Cómo ejecutar (desde la carpeta del repositorio)

No requiere paquetes externos para las multiplicaciones, pruebas ni mediciones.

```bash
# Probar una multiplicación concreta (recursiva por defecto)
python3 karatsuba.py 1234 5678

# Comparar multiplicación escolar y Karatsuba con umbral 8
python3 karatsuba.py 1234 5678 --metodo escuela
python3 karatsuba.py 1234 5678 --metodo karatsuba --umbral 8

# Ejecutar pruebas automáticas
python3 -m unittest discover -s tests -v

# Volver a calcular métricas T(N) y S(N) + CSV + informe
python3 benchmark.py --casos 3 --repeticiones 5
```

Para actualizar **gráficas opcionales**, instala `matplotlib` en tu entorno Python y ejecuta `python3 graficas.py`. Los PNG de ejemplo ya están incluidos en `resultados/`, así que **no necesitas matplotlib para ejecutar la solución**.

## 5. Evidencias y conclusiones

Consulta [resultados/INFORME.md](resultados/INFORME.md) para las tablas de tiempo, memoria y operaciones de cada variante. Cada número y producto exacto usado en las mediciones está documentado en [resultados/casos.csv](resultados/casos.csv). Las imágenes `tiempo.png`, `memoria.png` y `operaciones.png` ilustran la comparación.

**Conclusión:** Karatsuba reduce la cantidad de multiplicaciones recursivas de cuatro a tres. Su ventaja principal es la reducción asintótica del trabajo, de O(N²) a O(N^1.585), aunque la velocidad y la memoria observadas dependen del umbral y la implementación utilizada. Todas las variantes devuelven el mismo resultado exacto.
