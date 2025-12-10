from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional

from app.models.api_models import GraphDefinition, WorkflowRunRequest, WorkflowRunResponse
from app.engine import WorkflowEngine
from app.run_store import save_graph, get_graph, get_run
from app.workflows.summarization_workflow import create_summarization_workflow

app = FastAPI(title="Workflow Engine V2", description="Async/Sync Graph Engine")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Workflow Engine V2",
        "docs": "/docs"
    }

# Pre-load example workflow
sum_workflow = create_summarization_workflow()
save_graph(sum_workflow)

@app.post("/graph/create", response_model=Dict[str, str])
async def create_graph(definition: GraphDefinition):
    if get_graph(definition.id):
        raise HTTPException(status_code=400, detail=f"Graph {definition.id} already exists.")
    save_graph(definition)
    return {"graph_id": definition.id}

@app.post("/graph/run", response_model=WorkflowRunResponse)
async def run_graph(request: WorkflowRunRequest):
    graph_def = get_graph(request.graph_id)
    if not graph_def:
        raise HTTPException(status_code=404, detail=f"Graph {request.graph_id} not found.")

    engine = WorkflowEngine(graph_def)
    
    if request.run_mode == "async":
        run_id = await engine.run_async(request.initial_state, request.config)
        return WorkflowRunResponse(run_id=run_id, status="running")
    elif request.run_mode == "sync":
        run_data = await engine.run_sync(request.initial_state, request.config)
        return WorkflowRunResponse(
            run_id=run_data["run_id"],
            status=run_data["status"],
            state=run_data.get("state"),
            execution_log=run_data.get("execution_log"),
            error=run_data.get("error")
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid run_mode. Use 'async' or 'sync'.")

@app.get("/graph/state/{run_id}", response_model=WorkflowRunResponse)
async def get_run_state(run_id: str):
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    
    return WorkflowRunResponse(
        run_id=run_id,
        status=run_data["status"],
        state=run_data.get("state"),
        execution_log=run_data.get("execution_log"),
        error=run_data.get("error")
    )

@app.get("/graph/{graph_id}", response_model=GraphDefinition)
async def get_graph_def(graph_id: str):
    graph = get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    return graph
