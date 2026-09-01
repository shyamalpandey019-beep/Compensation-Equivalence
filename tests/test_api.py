# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "equivpay-engine"

def test_api_metadata():
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "supported_countries" in data
    assert "IN" in data["supported_countries"]
    assert "US" in data["supported_countries"]

def test_api_calculate():
    payload = {
        "gross_salary": 3500000,
        "country_code": "IN",
        "city_name": "Bangalore",
        "role": "Software Engineer",
        "include_parity": True
    }
    response = client.post("/api/v1/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["input"]["currency"] == "INR"
    assert "tax" in data
    assert "normalized" in data
    assert "benchmark" in data
    assert "parity_matrix" in data

def test_api_parity_endpoint():
    response = client.get("/api/v1/parity?gross_salary=150000&country_code=US&city_name=San%20Francisco")
    assert response.status_code == 200
    data = response.json()
    assert "parity_matrix" in data
    assert len(data["parity_matrix"]) == 4
