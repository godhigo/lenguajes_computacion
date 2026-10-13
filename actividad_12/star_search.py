import time
import sys

def solve_star(graph, origin, destination, limit, heuristics):
    start_time = time.perf_counter()
    h_start = heuristics.get(origin, 0)
    frontier = [(h_start, 0, origin, [origin])]
    visited = set()
    
    while frontier and len(visited) < limit:
        frontier.sort(key=lambda x: x[0])
        f_val, g_val, current_node, path = frontier.pop(0)
        
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
            cost = neighbor_info[1]
            
            if neighbor not in visited:
                new_g = g_val + cost
                h_neighbor = heuristics.get(neighbor, 0)
                new_f = new_g + h_neighbor
                frontier.append((new_f, new_g, neighbor, path + [neighbor]))
                
    end_time = time.perf_counter()
    return {
        "visited_nodes": len(visited),
        "solution_found": False,
        "path": [],
        "T_n": f"{(end_time - start_time) * 1000:.4f} ms",
        "S_n": f"{sys.getsizeof(visited) + sys.getsizeof(frontier)} bytes"
    }
