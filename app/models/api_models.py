from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NodeDefinition(BaseModel):
    id: str
    action_name: str
    config: Dict[str, Any] = {}

class EdgeDefinition(BaseModel):
    source_id: str
    target_id: str
    condition_name: Optional[str] = None
    loop: bool = False

class GraphDefinition(BaseModel):
    id: str
    start_node_id: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]

class WorkflowRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = {}
    run_mode: str = "async" # "async" or "sync"
    config: Dict[str, Any] = {}

class ExecutionLogEntry(BaseModel):
    node_id: str
    start_ts: datetime
    end_ts: datetime
    state_snapshot: Dict[str, Any]

class WorkflowRunResponse(BaseModel):
    run_id: str
    status: str # 'running', 'completed', 'failed'
    state: Optional[Dict[str, Any]] = None
    execution_log: Optional[List[ExecutionLogEntry]] = None
    error: Optional[str] = None
