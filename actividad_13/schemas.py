from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class GraphRequest(BaseModel):
    graph: Dict[str, List[List[Any]]]
    origin: str
    destination: Optional[str] = None
    
class GraphGenRequest(BaseModel):
    num_nodes: int
    is_directed: bool = False
    complete: bool = True
