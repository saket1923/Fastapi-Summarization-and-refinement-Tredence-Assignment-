# FastAPI Workflow Engine (V2)
![image alt](https://github.com/saket1923/Fastapi-Summarization-and-refinement-Tredence-Assignment-/blob/3bb0980e4cc492fb46fde2019c89b7c730bb7c51/Screenshot%202025-12-10%20203127.png)


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
