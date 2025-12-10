from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_summarization_workflow():
    print("Testing Summarization Workflow...")
    
    payload = {
        "graph_id": "summarization_workflow",
        "initial_state": {
            "input_text": "This is a long text that needs to be split and summarized. It should be long enough to trigger the split logic. Let's add more words to make sure it is long enough. Repeated words for length. Length is important here.",
            "limit": 20
        }
    }
    
    response = client.post("/graph/run", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\nWorkflow Run Successful!")
        print(f"Run ID: {data['run_id']}")
        print(f"Status: {data['status']}")
        print(f"Final Summary: {data['state'].get('summary')}")
        print(f"Execution Log: {data['execution_log']}")
        
        # Basic validation
        assert data['status'] == 'completed'
        assert 'summary' in data['state']
        assert len(data['state']['summary']) <= 20
        print("\nValidation Passed: Summary length is within limit.")
    else:
        print(f"\nWorkflow Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_summarization_workflow()
