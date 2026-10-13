import random
import string

def generate_synthetic_graph(num_nodes: int, is_directed: bool, complete: bool):
    nodes = [string.ascii_uppercase[i] for i in range(num_nodes)]
    graph = {node: [] for node in nodes}
    
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                if not is_directed and i > j:
                    continue
                if complete or random.random() > 0.3:
                    weight = random.randint(10, 100)
                    graph[nodes[i]].append([nodes[j], weight])
                    if not is_directed:
                        graph[nodes[j]].append([nodes[i], weight])
    return graph
