# Resultados experimentales: Actividad 14

Ejecutado (UTC): **2026-10-28 18:18:24**.  
Python: **3.13.5**. Sistema: **Linux x86_64**.  
Datos: **3 pares pseudoaleatorios por tamaño**, semilla fija 2026.  
Tiempos: **mediana de 5 ejecuciones por par**; la tabla presenta el promedio de esas medianas.

## T(N): tiempo y cantidad de operaciones

| Dígitos por operando | Variante | Tiempo medio (ms) | Productos de dígitos (prom.) | Llamadas (prom.) | Prof. máx. (prom.) |
| ---: | :--- | ---: | ---: | ---: | ---: |
| 20 | Escuela | 0.0673 | 400.0 | 1.0 | 0.0 |
| 20 | Divide4 | 1.3062 | 348.3 | 762.3 | 5.0 |
| 20 | Karatsuba u=1 | 1.0863 | 190.7 | 365.0 | 6.0 |
| 20 | Karatsuba u=8 | 0.1724 | 263.0 | 13.0 | 2.0 |
| 20 | Karatsuba u=16 | 0.1173 | 321.0 | 4.0 | 1.0 |
| 50 | Escuela | 0.4768 | 2500.0 | 1.0 | 0.0 |
| 50 | Divide4 | 7.4824 | 1995.7 | 4145.0 | 6.0 |
| 50 | Karatsuba u=1 | 4.3272 | 735.7 | 1486.0 | 8.0 |
| 50 | Karatsuba u=8 | 0.7298 | 1133.0 | 40.0 | 3.0 |
| 50 | Karatsuba u=16 | 0.4776 | 1450.3 | 13.0 | 2.0 |
| 100 | Escuela | 1.6197 | 10000.0 | 1.0 | 0.0 |
| 100 | Divide4 | 27.9571 | 8313.3 | 17117.0 | 7.0 |
| 100 | Karatsuba u=1 | 12.5590 | 2292.7 | 4517.0 | 9.0 |
| 100 | Karatsuba u=8 | 2.0003 | 3447.7 | 121.0 | 4.0 |
| 100 | Karatsuba u=16 | 1.5338 | 4383.7 | 40.0 | 3.0 |

## S(N): memoria adicional observada

| Dígitos por operando | Variante | Pico medio (KiB) |
| ---: | :--- | ---: |
| 20 | Escuela | 2.631 |
| 20 | Divide4 | 3.306 |
| 20 | Karatsuba u=1 | 3.267 |
| 20 | Karatsuba u=8 | 3.249 |
| 20 | Karatsuba u=16 | 3.244 |
| 50 | Escuela | 6.091 |
| 50 | Divide4 | 7.089 |
| 50 | Karatsuba u=1 | 7.131 |
| 50 | Karatsuba u=8 | 7.068 |
| 50 | Karatsuba u=16 | 7.068 |
| 100 | Escuela | 11.790 |
| 100 | Divide4 | 13.303 |
| 100 | Karatsuba u=1 | 13.345 |
| 100 | Karatsuba u=8 | 13.282 |
| 100 | Karatsuba u=16 | 13.282 |

## Interpretación

- **Escuela** realiza n² multiplicaciones de dígitos cuando los dos números tienen n dígitos.
- **Divide4** utiliza cuatro subproblemas: T(n)=4T(n/2)+O(n), del orden O(n²).
- **Karatsuba** utiliza tres: T(n)=3T(n/2)+O(n), del orden O(n^1.585).
- Un umbral 8 o 16 aplica la multiplicación tradicional en subproblemas pequeños; la recurrencia superior sigue siendo la de Karatsuba.
- **S(n)** teórica de las versiones recursivas, incluyendo temporales, es O(n), con profundidad de pila O(log n); la implementación escolar usa O(n) para el resultado.
- `tracemalloc` mide **memoria rastreada por Python durante esa operación**, no la RAM total del proceso. Sus cifras dependen del intérprete y las condiciones de ejecución.
- El tiempo real puede favorecer a Escuela para tamaños pequeños debido al costo de la recursión y de manipular cadenas en Python, aunque Karatsuba reduzca productos de dígitos.
- Todas las operaciones fueron verificadas frente a `int(a) * int(b)` **sólo como referencia**; las implementaciones analizadas no usan ese producto nativo.

Para repetir: `python3 benchmark.py --casos 3 --repeticiones 5`.
Los datos por caso están en `mediciones.csv` y los operandos/productos en `casos.csv`.
