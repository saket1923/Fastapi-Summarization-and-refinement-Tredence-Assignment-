from typing import Dict, Any, Optional
from app.models.api_models import GraphDefinition

# In-memory storage
_graphs: Dict[str, GraphDefinition] = {}
_runs: Dict[str, Dict[str, Any]] = {}

def save_graph(graph: GraphDefinition):
    _graphs[graph.id] = graph

def get_graph(graph_id: str) -> Optional[GraphDefinition]:
    return _graphs.get(graph_id)

def save_run(run_id: str, data: Dict[str, Any]):
    _runs[run_id] = data

def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    return _runs.get(run_id)

def update_run(run_id: str, updates: Dict[str, Any]):
    if run_id in _runs:
        _runs[run_id].update(updates)
