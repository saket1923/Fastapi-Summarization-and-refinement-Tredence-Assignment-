from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_run_workflow_sync():
    """
    Test the summarization workflow in synchronous mode.
    """
   
    
    # 2. Run Workflow
    long_text = "This is a sentence. " * 50 # 50 sentences, definitely > 100 chars
    max_length = 50
    
    payload = {
        "graph_id": "summarization_workflow",
        "initial_state": {
            "text": long_text,
            "max_length": max_length
        },
        "run_mode": "sync",
        "config": {
            "max_iterations": 20
        }
    }
    
    response = client.post("/graph/run", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "completed"
    assert data["run_id"] is not None
    
    final_state = data["state"]
    final_summary = final_state.get("final_summary")
    
    assert final_summary is not None
    assert len(final_summary) <= max_length
    
    
    log = data["execution_log"]
    assert len(log) > 0
    node_ids = [entry["node_id"] for entry in log]
    
    
    assert "split_text" in node_ids
    assert "summarize_chunks" in node_ids
    assert "merge_summaries" in node_ids
    assert "refine_final_summary" in node_ids

if __name__ == "__main__":
    test_run_workflow_sync()
    print("Test passed!")
