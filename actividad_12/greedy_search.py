import time
import sys

def solve_greedy(graph, origin, destination, limit, heuristics):
    start_time = time.perf_counter()
    frontier = [(heuristics.get(origin, 0), origin, [origin])]
    visited = set()
    
    while frontier and len(visited) < limit:
        frontier.sort(key=lambda x: x[0])
        h_val, current_node, path = frontier.pop(0)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        if current_node == destination:
            end_time = time.perf_counter()
            return {
                "visited_nodes": len(visited),
                "solution_found": True,
                "path": path,
                "T_n": f"{(end_time - start_time) * 1000:.4f} ms",
                "S_n": f"{sys.getsizeof(visited) + sys.getsizeof(frontier)} bytes"
            }
            
        neighbors = graph.get(current_node, [])
        for neighbor_info in neighbors:
            neighbor = neighbor_info[0]
            if neighbor not in visited:
                h_neighbor = heuristics.get(neighbor, 0)
                frontier.append((h_neighbor, neighbor, path + [neighbor]))
                
    end_time = time.perf_counter()
    return {
        "visited_nodes": len(visited),
        "solution_found": False,
        "path": [],
        "T_n": f"{(end_time - start_time) * 1000:.4f} ms",
        "S_n": f"{sys.getsizeof(visited) + sys.getsizeof(frontier)} bytes"
    }
