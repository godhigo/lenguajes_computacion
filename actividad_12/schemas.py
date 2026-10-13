from pydantic import BaseModel, root_validator
from typing import Dict, List, Optional, Any

class GraphRequest(BaseModel):
    graph: Dict[str, List[List[Any]]]
    origin: str
    destination: str
    limit: Optional[int] = None
    heuristics: Optional[Dict[str, float]] = {}

    @root_validator(pre=True)
    def calculate_limit(cls, values):
        graph = values.get('graph')
        limit = values.get('limit')
        if graph and limit is None:
            values['limit'] = int(len(graph) * 0.8)
        return values
