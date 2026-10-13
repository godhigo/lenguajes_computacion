# Actividad 11: Implementación de Búsquedas Informadas (Greedy y A*)

**Datos de Identificación:**
*   **Nombre:** Diego Navarro Sánchez
*   **Materia/Actividad:** Actividad 11 - Búsqueda Informada en Grafos

## Descripción de la Implementación
Se desarrolló una API REST utilizando FastAPI (Backend) con dos endpoints principales (`/search/greedy` y `/search/star`) que procesan estructuras de grafos mediante Pydantic. Los algoritmos fueron implementados desde cero sin depender de librerías especializadas, utilizando listas dinámicas ordenadas iterativamente para simular colas de prioridad. 

*   **Greedy Best-First Search:** Selecciona el siguiente nodo basándose exclusivamente en una heurística h(n), priorizando la velocidad de exploración.
*   **A* (Estrella):** Selecciona el siguiente nodo evaluando f(n) = g(n) + h(n), balanceando el costo real acumulado g(n) y la estimación a la meta h(n).

El límite de nodos a visitar se configuró dinámicamente al 80% de los nodos totales del grafo introducido, si no se especifica uno. Los cálculos de complejidad empírica se midieron mediante `time.perf_counter()` para T(n) y `sys.getsizeof()` para S(n).

## Pruebas y Resultados
Las pruebas se realizaron sobre tres grafos de distinta complejidad. Se establecieron heurísticas h(n) estimadas hacia los nodos destino para evaluar la toma de decisiones.

### 1. Grafo de 10 Nodos (Origen: A -> Destino: J)
*   **Greedy:** Solución True. El algoritmo tendió a explorar profundamente de inmediato. T(n) de ~0.0150 ms.
*   **A*:** Solución True. Evaluó rutas alternativas contrastando los costos declarados. T(n) se mantuvo marginalmente superior a Greedy debido a los cálculos aditivos de g(n).

### 2. Grafo de 25 Nodos (Origen: A -> Destino: Y)
*   **Greedy:** Demostró el compromiso de optimalidad. Avanzó rápidamente hacia nodos intermedios, pero se topó con costos reales altos, demostrando cómo h(n) por sí sola puede engañar al algoritmo.
*   **A*:** Ruta óptima garantizada. Evitó rutas de alto costo priorizando caminos con menor costo acumulado, manteniendo un S(n) mayor que Greedy.

### 3. Grafo de 50 Nodos (Origen: A -> Destino: AX)
*   **Greedy:** Alcanzó la meta visitando significativamente menos nodos que A*. El límite del 80% (40 nodos) no fue un problema. T(n) destacó por su eficiencia de exploración.
*   **A*:** La complejidad espacial S(n) incrementó radicalmente ya que A* tuvo que almacenar y re-evaluar múltiples trayectorias antes de confirmar que rutas sub-óptimas no debían expandirse. Logró la ruta óptima demostrando el compromiso clásico: mayor gasto de memoria y tiempo a cambio de garantía matemática.

## Conclusión Analítica
Greedy es superior cuando el objetivo es encontrar cualquier ruta válida minimizando T(n) y S(n) en arquitecturas saturadas. Sin embargo, para sistemas donde el costo de la ruta es vital, A* es imperativo, a costa de una complejidad que crece exponencialmente dependiendo del factor de ramificación.
