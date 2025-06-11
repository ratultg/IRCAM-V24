"""
End-to-end integration test for IR Thermal Monitoring System backend.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app, get_sensor
from backend.src.zones import ZonesManager
from backend.src.alarms import AlarmManager
from backend.src.frames import ThermalFrameBuffer, EventTriggeredStorage
import datetime

client = TestClient(app)

def test_full_workflow(monkeypatch):
    # Patch sensor to return a predictable frame
    class DummySensor:
        def read_frame(self):
            return [10.0] * 768
    monkeypatch.setattr("backend.src.main._sensor_instance", DummySensor())

    # Add a zone
    resp = client.post("/api/v1/zones", json={"id": 1, "x": 0, "y": 0, "width": 2, "height": 2})
    assert resp.status_code == 200
    # Get real-time frame
    resp = client.get("/api/v1/thermal/real-time")
    assert resp.status_code == 200
    frame = resp.json()["frame"]
    assert len(frame) == 768
    # Get zone average
    resp = client.get("/api/v1/zones/1/average")
    assert resp.status_code == 200
    avg = resp.json()["average"]
    assert avg == 10.0
    # Health check
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
