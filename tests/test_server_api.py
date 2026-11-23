"""
Unit and integration tests for StegoGuard FastAPI REST endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["version"] == "2.0.0"

def test_api_generate_keys():
    response = client.post("/api/verification/generate-keys")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "BEGIN RSA PRIVATE KEY" in data["private_key"] or "BEGIN PRIVATE KEY" in data["private_key"]
    assert "BEGIN PUBLIC KEY" in data["public_key"]

def test_api_hash_text():
    response = client.post("/api/verification/hash", data={"text": "StegoGuard Test Message"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["computed_hash"]) == 64

def test_api_analytics():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "metrics" in data

def test_api_audit_logs():
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "records" in data
