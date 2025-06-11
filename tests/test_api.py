"""
API integration tests for FastAPI endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app, get_sensor
from backend.src import main as main_module

@pytest.fixture(autouse=True)
def patch_sensor(monkeypatch):
    class DummySensor:
        def read_frame(self):
            return [42.0] * 768
    monkeypatch.setattr(main_module, "_sensor_instance", DummySensor())

client = TestClient(app)

def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_zone_crud():
    # Add zone
    resp = client.post("/api/v1/zones", json={"id": 1, "x": 0, "y": 0, "width": 2, "height": 2, "name": "Test Zone", "color": "#00FF00"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Zone"
    assert data["color"] == "#00FF00"
    # List zones
    resp = client.get("/api/v1/zones")
    assert resp.status_code == 200
    zones = resp.json()
    assert len(zones) >= 1
    assert zones[0]["name"] == "Test Zone"
    assert zones[0]["color"] == "#00FF00"
    # Delete zone
    resp = client.delete("/api/v1/zones/1")
    assert resp.status_code == 200
    # Delete non-existent zone
    resp = client.delete("/api/v1/zones/99")
    assert resp.status_code == 404

def test_real_time_frame():
    resp = client.get("/api/v1/thermal/real-time")
    assert resp.status_code == 200
    data = resp.json()
    assert "frame" in data and len(data["frame"]) == 768
    assert "timestamp" in data
