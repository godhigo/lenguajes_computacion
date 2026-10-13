import time
import sys

def solve_tsp_exact(graph, origin):
    start_time = time.perf_counter()
    nodes = list(graph.keys())
    
    min_cost = float('inf')
    best_path = []
    visited_states = 0
    
    # Backtracking DFS para evaluar combinaciones
    def dfs(current_node, visited, current_cost, path):
        nonlocal min_cost, best_path, visited_states
        visited_states += 1
        
        # Poda (Branch and Bound): Si ya superamos el mínimo, abortar esta rama
        if current_cost >= min_cost:
            return
            
        if len(visited) == len(nodes):
            for neighbor_info in graph.get(current_node, []):
                if neighbor_info[0] == origin:
                    total_cost = current_cost + neighbor_info[1]
                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_path = path + [origin]
            return
            
        for neighbor_info in graph.get(current_node, []):
            neighbor, weight = neighbor_info[0], neighbor_info[1]
            if neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, visited, current_cost + weight, path + [neighbor])
                visited.remove(neighbor)

    dfs(origin, {origin}, 0, [origin])
    end_time = time.perf_counter()
    
    return {
        "tiempo_ejecucion_ms": (end_time - start_time) * 1000,
        "memoria_consumida_bytes": sys.getsizeof(best_path),
        "nodos_recorridos": visited_states,
        "costo_camino": min_cost if min_cost != float('inf') else 0,
        "ruta": best_path
    }

def solve_tsp_greedy(graph, origin):
    start_time = time.perf_counter()
    nodes = list(graph.keys())
    unvisited = set(nodes)
    unvisited.remove(origin)
    
    current_node = origin
    path = [origin]
    total_cost = 0
    visited_count = 1
    
    while unvisited:
        neighbors = graph.get(current_node, [])
        valid_neighbors = [n for n in neighbors if n[0] in unvisited]
        
        if not valid_neighbors:
            break
            
        # Elige al vecino con menor peso
        best_neighbor = min(valid_neighbors, key=lambda x: x[1])
        next_node = best_neighbor[0]
        cost = best_neighbor[1]
        
        path.append(next_node)
        total_cost += cost
        unvisited.remove(next_node)
        current_node = next_node
        visited_count += 1
        
    for neighbor_info in graph.get(current_node, []):
        if neighbor_info[0] == origin:
            path.append(origin)
            total_cost += neighbor_info[1]
            break
            
    end_time = time.perf_counter()
    return {
        "tiempo_ejecucion_ms": (end_time - start_time) * 1000,
        "memoria_consumida_bytes": sys.getsizeof(unvisited) + sys.getsizeof(path),
        "nodos_recorridos": visited_count,
        "costo_camino": total_cost,
        "ruta": path
    }
