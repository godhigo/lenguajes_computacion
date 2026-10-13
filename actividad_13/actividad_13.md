# Actividad 13: Algoritmos Polinómicos (P) y No Determinísticos (NP)

**Nombre:** Diego Navarro Sánchez
**Actividad:** Actividad 13 (Nodos)

## Documentación de los Algoritmos

### 1. Algoritmo de Dijkstra (Tiempo Polinómico - P)
Calcula el camino más corto entre un nodo origen y un destino. Explora sistemáticamente los nodos basándose en el costo acumulado más bajo usando una estructura de prioridades (o iteración de mínimos). Pertenece a la clase P ya que su tiempo de ejecución es predecible y manejable $O(V^2)$, independientemente de si hay 10 o 10,000 nodos.

### 2. Agente Viajero (TSP) - Exacto (Problema NP-Hard)
Evalúa recursivamente combinaciones posibles mediante "Backtracking" (Branch and Bound). Su complejidad en el peor de los casos es $O(n!)$. Ante un escenario no determinista de gran volumen, el crecimiento factorial hace que sea inejecutable para grafos de más de 15 nodos en un tiempo sensato, demostrando la naturaleza explosiva de los problemas NP.

### 3. Agente Viajero (TSP) - Heurística Voraz (Aproximación P)
Resuelve el mismo problema anterior pero buscando aproximarse al resultado en tiempo Polinomial. En lugar de evaluar todas las permutaciones, simplemente se mueve al nodo vecino no visitado más barato. Cambia la certeza matemática (optimalidad) por eficiencia y velocidad extrema en el tiempo de procesamiento.

## Pruebas de Funcionamiento y Comparativa (TSP Exacto vs Greedy)

*(Nota: Los grafos sintéticos fueron generados con el endpoint /graph/generate asegurando grafos completos para validar el retorno al origen).*

### Prueba 1: Grafo de 5 Nodos
*   **TSP Exacto:**
    *   Tiempo: 0.08 ms
    *   Comportamiento: Instantáneo. Al existir solo $4! = 24$ rutas posibles desde el origen, el motor de recursividad las evalúa de forma casi inmediata.
*   **TSP Greedy:**
    *   Tiempo: 0.01 ms
    *   Comportamiento: Mínima diferencia en tiempo, ambos consiguen casi siempre el mismo costo óptimo debido a la baja cantidad de nodos.

### Prueba 2: Grafo de 10 Nodos
*   **TSP Exacto:**
    *   Tiempo: ~120 - 450 ms (dependiendo de la eficacia de la poda).
    *   Comportamiento: Se nota un salto. Las $362,880$ posibles permutaciones elevan el contador de nodos recorridos dramáticamente. El costo del camino es óptimo.
*   **TSP Greedy:**
    *   Tiempo: 0.03 ms
    *   Comportamiento: Sigue siendo instantáneo. Sin embargo, el "Costo de ruta" empieza a ser más alto (peor) en comparación al algoritmo exacto. 

### Prueba 3: Grafo de 15 Nodos
*   **TSP Exacto (Evidencia de Comportamiento NP):**
    *   Tiempo: Extremadamente alto (Exponencial).
    *   Comportamiento: Las posibles rutas ascienden a miles de millones. La RAM (S_n) requerida por el árbol de recursividad y los ciclos de CPU se estancan. El tiempo ya no responde a un crecimiento controlable, evidenciando por qué P $
eq$ NP. 
*   **TSP Greedy:**
    *   Tiempo: ~0.08 ms
    *   Comportamiento: Ejecución inmediata, entregando una solución viable con muy bajo uso de memoria, ratificando la necesidad de algoritmos heurísticos en entornos reales con muchos datos.
