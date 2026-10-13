from fastapi import FastAPI
from schemas import GraphRequest, GraphGenRequest
from dijkstra import solve_dijkstra
from tsp import solve_tsp_exact, solve_tsp_greedy
from graph_generator import generate_synthetic_graph

app = FastAPI(title="Graph Search API - Actividad 12")

@app.post("/search/dijkstra")
def endpoint_dijkstra(request: GraphRequest):
    return solve_dijkstra(request.graph, request.origin, request.destination)

@app.post("/search/tsp/exact")
def endpoint_tsp_exact(request: GraphRequest):
    return solve_tsp_exact(request.graph, request.origin)

@app.post("/search/tsp/greedy")
def endpoint_tsp_greedy(request: GraphRequest):
    return solve_tsp_greedy(request.graph, request.origin)

@app.post("/graph/generate")
def endpoint_generate_graph(request: GraphGenRequest):
    return generate_synthetic_graph(request.num_nodes, request.is_directed, request.complete)
