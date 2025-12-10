# FastAPI Workflow Engine (V2)

This implementation follows the assignment described in the uploaded prompt (brief one-liner) and include a reference marker: :contentReference[oaicite:0]{index=0}

A complete, runnable FastAPI project implementing a minimal workflow/graph engine with a "Text Summarization + Refinement" example.

## Features
- **Workflow Engine**: Supports nodes, edges, branching, and looping.
- **Async/Sync Execution**: Run workflows in the background or wait for results.
- **Rule-Based Tools**: Includes text splitting, summarization, merging, and refinement tools.
- **In-Memory Storage**: Tracks graphs and execution runs.

## Project Structure
- `app/engine.py`: Core workflow engine.
- `app/registry.py`: Tool and condition registry.
- `app/workflows/`: Workflow definitions (e.g., `summarization_workflow.py`).
- `app/models/`: Pydantic models.
- `app/main.py`: FastAPI application.

## Setup & Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Run Tests**:
   ```bash
   pytest tests/test_run_workflow.py
   ```

## API Usage

### Create Graph (Optional - Pre-loaded)
`POST /graph/create`

### Run Workflow (Sync)
`POST /graph/run`
```json
{
  "graph_id": "summarization_workflow",
  "initial_state": {
    "text": "Long text here...",
    "max_length": 50
  },
  "run_mode": "sync"
}
```

### Run Workflow (Async)
`POST /graph/run`
```json
{
  "graph_id": "summarization_workflow",
  "initial_state": {
    "text": "Long text here...",
    "max_length": 50
  },
  "run_mode": "async"
}
```
Response: `{"run_id": "..."}`

### Get Run State
`GET /graph/state/{run_id}`
