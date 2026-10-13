from fastapi import FastAPI
from schemas import GraphRequest
from greedy_search import solve_greedy
from star_search import solve_star

app = FastAPI(title="Graph Search API - Actividad 11")

@app.post("/search/greedy")
def greedy_endpoint(request: GraphRequest):
    return solve_greedy(
        graph=request.graph,
        origin=request.origin,
        destination=request.destination,
        limit=request.limit,
        heuristics=request.heuristics
    )

@app.post("/search/star")
def star_endpoint(request: GraphRequest):
    return solve_star(
        graph=request.graph,
        origin=request.origin,
        destination=request.destination,
        limit=request.limit,
        heuristics=request.heuristics
    )
