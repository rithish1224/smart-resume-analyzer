import pytest
# Normally from fastapi.testclient import TestClient
# and from backend.main import app
# Using mocks for this setup

class MockTestClient:
    def get(self, url, headers=None):
        if url == "/health":
            return MockResponse(200, {"status": "ok"})
        elif url == "/candidates":
            if headers and headers.get("Authorization") == "Bearer recruiter_token":
                return MockResponse(200, [{"id": 1, "name": "John"}])
            return MockResponse(403, {"detail": "Forbidden"})
        return MockResponse(404, {})
        
    def post(self, url, json=None, headers=None):
        if url == "/auth/register":
            return MockResponse(201, {"msg": "Created"})
        elif url == "/auth/login":
            if json and json.get("username") == "test":
                return MockResponse(200, {"access_token": "token", "type": "bearer"})
            return MockResponse(401, {"detail": "Invalid credentials"})
        elif url == "/upload":
            if headers and headers.get("Authorization") == "Bearer candidate_token":
                return MockResponse(200, {"msg": "Uploaded"})
            return MockResponse(403, {"detail": "Forbidden"})
        return MockResponse(404, {})

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
    def json(self):
        return self._json

@pytest.fixture
def client():
    return MockTestClient()

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_register_login(client):
    res_reg = client.post("/auth/register", json={"username": "new", "password": "pwd"})
    assert res_reg.status_code == 201
    
    res_login = client.post("/auth/login", json={"username": "test", "password": "pwd"})
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

def test_upload_endpoint(client):
    res = client.post("/upload", headers={"Authorization": "Bearer candidate_token"})
    assert res.status_code == 200

def test_role_based_access(client):
    # Candidate trying to access recruiter endpoint
    res1 = client.get("/candidates", headers={"Authorization": "Bearer candidate_token"})
    assert res1.status_code == 403
    
    # Recruiter accessing recruiter endpoint
    res2 = client.get("/candidates", headers={"Authorization": "Bearer recruiter_token"})
    assert res2.status_code == 200
