import pytest
from fastapi.testclient import TestClient
from DatabaseCreator.api import app

# Create a test client
client = TestClient(app)

# Test payload
test_payload = {
    "must_contain": ["developpeur", "python"],
    "exact_match": False
}

# Test case using real database
def test_search_jobs():
    response = client.post("/search/", json=test_payload)
    
    assert response.status_code == 200
    
    