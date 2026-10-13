import time
import sys

def solve_dijkstra(graph, origin, destination):
    start_time = time.perf_counter()
    
    distances = {node: float('inf') for node in graph}
    distances[origin] = 0
    previous = {node: None for node in graph}
    
    unvisited = list(graph.keys())
    visited_nodes_count = 0
    
    while unvisited:
        current_node = min(unvisited, key=lambda node: distances[node])
        unvisited.remove(current_node)
        visited_nodes_count += 1
        
        if distances[current_node] == float('inf') or current_node == destination:
            break
            
        for neighbor_info in graph.get(current_node, []):
            neighbor, weight = neighbor_info[0], neighbor_info[1]
            if neighbor in unvisited:
                new_dist = distances[current_node] + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    
    path = []
    curr = destination
    while curr is not None:
        path.insert(0, curr)
        curr = previous[curr]
        
    end_time = time.perf_counter()
    
    if len(path) == 0 or path[0] != origin:
        return {"error": "No hay ruta"}
        
    return {
        "tiempo_ejecucion_ms": (end_time - start_time) * 1000,
        "memoria_consumida_bytes": sys.getsizeof(distances) + sys.getsizeof(previous),
        "nodos_recorridos": visited_nodes_count,
        "costo_camino": distances[destination],
        "ruta": path
    }
