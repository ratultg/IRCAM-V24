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
import tempfile
from backend.src.database import Database
from backend.src.main import get_db

class DummySensor:
    def read_frame(self):
        return [42.0] * 768

@pytest.fixture(autouse=True)
def patch_sensor(monkeypatch):
    app.dependency_overrides[get_sensor] = lambda: DummySensor()
    yield
    app.dependency_overrides.pop(get_sensor, None)

@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    tf = tempfile.NamedTemporaryFile(delete=False)
    db = Database(tf.name)
    db.connect()
    db.initialize_schema()
    app.dependency_overrides[get_db] = lambda: db
    yield
    db.close()
    tf.close()
    os.unlink(tf.name)
    app.dependency_overrides.pop(get_db, None)

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

def test_frames_export_csv():
    # Insert a dummy event and frame
    db = app.dependency_overrides[get_db]()
    db.execute_query("INSERT INTO alarm_events (id, zone_id, timestamp, temperature, alarm_id) VALUES (?, ?, ?, ?, ?)", (1, 1, "2025-06-12T12:00:00Z", 42.0, 1))
    import numpy as np
    arr = (np.ones((24,32), dtype=np.float32) * 42.0).tobytes()
    db.execute_query("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, ?, ?, ?)", (1, "2025-06-12T12:00:00Z", arr, len(arr)))
    client = TestClient(app)
    resp = client.get("/api/v1/frames/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    content = resp.content.decode()
    # Only metadata columns expected: id, event_id, timestamp, frame_size
    assert "timestamp" in content and "frame_size" in content and "pixel_0" not in content

def test_frames_export_overlay_stats():
    db = app.dependency_overrides[get_db]()
    db.execute_query("INSERT INTO alarm_events (id, zone_id, timestamp, temperature, alarm_id) VALUES (?, ?, ?, ?, ?)", (1, 1, "2025-06-12T12:00:00Z", 42.0, 1))
    import numpy as np
    arr = (np.ones((24,32), dtype=np.float32) * 42.0).tobytes()
    db.execute_query("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, ?, ?, ?)", (1, "2025-06-12T12:00:00Z", arr, len(arr)))
    client = TestClient(app)
    resp = client.get("/api/v1/frames/export?overlay=stats")
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "mean" in content and "std" in content and "frame_size" in content

def test_settings_crud():
    # Set a setting
    resp = client.post("/api/v1/settings", json={"key": "test_key", "value": "test_value", "description": "desc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["key"] == "test_key"
    assert data["value"] == "test_value"
    assert data["description"] == "desc"
    # Get all settings
    resp = client.get("/api/v1/settings")
    assert resp.status_code == 200
    settings = resp.json()
    assert any(s["key"] == "test_key" and s["value"] == "test_value" for s in settings)

def test_database_backup_restore_and_migrate():
    # Backup
    resp = client.post("/api/v1/database/backup")
    assert resp.status_code == 200
    backup_data = resp.content
    assert len(backup_data) > 1000  # Should be a non-trivial SQLite file
    # Restore
    files = {"file": ("backup_test.db", backup_data, "application/octet-stream")}
    resp = client.post("/api/v1/database/restore", files=files)
    assert resp.status_code == 200
    assert resp.json()["status"] == "restored"
    # Migrate
    resp = client.post("/api/v1/database/migrate")
    assert resp.status_code == 200
    assert resp.json()["status"] == "migrated"

def test_analytics_heatmap_trends_anomalies():
    # Insert dummy zone and data
    db = app.dependency_overrides[get_db]()
    db.execute_query("INSERT INTO zones (id, x, y, width, height, name, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (1, 0, 0, 32, 24, 'Test Zone', '#00FF00'))
    # Insert thermal_data for a range
    import datetime
    now = datetime.datetime.utcnow()
    for i in range(10):
        ts = (now.replace(microsecond=0) - datetime.timedelta(minutes=10-i)).isoformat()
        temp = 20.0 + i
        db.execute_query("INSERT INTO thermal_data (zone_id, timestamp, temperature) VALUES (?, ?, ?)", (1, ts, temp))
    client = TestClient(app)
    start = (now.replace(microsecond=0) - datetime.timedelta(minutes=10)).isoformat()
    end = now.replace(microsecond=0).isoformat()
    # Heatmap
    resp = client.get(f"/api/v1/analytics/heatmap?start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["width"] == 32 and data["height"] == 24
    assert isinstance(data["heatmap"], list)
    # Trends
    resp = client.get(f"/api/v1/analytics/trends?start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["timestamps"]) == 10
    assert len(data["values"]) == 10
    # Anomalies
    resp = client.get(f"/api/v1/analytics/anomalies?start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert "anomalies" in data

def test_reports_endpoint():
    db = app.dependency_overrides[get_db]()
    db.execute_query("INSERT INTO zones (id, x, y, width, height, name, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (1, 0, 0, 32, 24, 'Test Zone', '#00FF00'))
    import datetime
    now = datetime.datetime.utcnow()
    for i in range(10):
        ts = (now.replace(microsecond=0) - datetime.timedelta(minutes=10-i)).isoformat()
        temp = 20.0 + i
        db.execute_query("INSERT INTO thermal_data (zone_id, timestamp, temperature) VALUES (?, ?, ?)", (1, ts, temp))
    client = TestClient(app)
    start = (now.replace(microsecond=0) - datetime.timedelta(minutes=10)).isoformat()
    end = now.replace(microsecond=0).isoformat()
    # Summary report
    resp = client.get(f"/api/v1/reports?report_type=summary&start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_type"] == "summary"
    assert "mean" in data["summary"]
    # Trend report
    resp = client.get(f"/api/v1/reports?report_type=trend&start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_type"] == "trend"
    assert "timestamps" in data["summary"]
    # Anomaly count report
    resp = client.get(f"/api/v1/reports?report_type=anomaly_count&start_time={start}&end_time={end}&zone_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_type"] == "anomaly_count"
    assert "anomaly_count" in data["summary"]

def test_alarm_history_and_acknowledge():
    db = app.dependency_overrides[get_db]()
    # Insert a zone and alarm
    db.execute_query("INSERT INTO zones (id, x, y, width, height, name, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (1, 0, 0, 32, 24, 'Test Zone', '#00FF00'))
    db.execute_query("INSERT INTO alarms (id, zone_id, threshold, enabled) VALUES (?, ?, ?, ?)", (1, 1, 25.0, 1))
    # Insert an alarm event
    db.execute_query("INSERT INTO alarm_events (id, zone_id, timestamp, temperature, alarm_id) VALUES (?, ?, ?, ?, ?)", (1, 1, "2025-06-12T12:00:00Z", 30.0, 1))
    client = TestClient(app)
    # Test alarm history endpoint
    resp = client.get("/api/v1/alarms/history")
    assert resp.status_code == 200
    events = resp.json()
    assert any(e["alarm_id"] == 1 and e["zone_id"] == 1 for e in events)
    # Test acknowledge endpoint
    resp = client.post("/api/v1/alarms/acknowledge", json={"alarm_id": 1})
    assert resp.status_code == 200
    # Check that alarm is acknowledged in history
    resp = client.get("/api/v1/alarms/history")
    assert resp.status_code == 200
    events = resp.json()
    ack_event = next((e for e in events if e["alarm_id"] == 1), None)
    assert ack_event is not None and ack_event["acknowledged"] is True

def test_event_frame_blobs():
    db = app.dependency_overrides[get_db]()
    # Insert a zone, event, and frames
    db.execute_query("INSERT INTO zones (id, x, y, width, height, name, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (1, 0, 0, 32, 24, 'Test Zone', '#00FF00'))
    event_id = 42
    db.execute_query("INSERT INTO alarm_events (id, zone_id, timestamp, temperature, alarm_id) VALUES (?, ?, ?, ?, ?)", (event_id, 1, "2025-06-12T12:00:00Z", 42.0, 1))
    import numpy as np
    arr1 = (np.ones((24,32), dtype=np.float32) * 10.0).tobytes()
    arr2 = (np.ones((24,32), dtype=np.float32) * 20.0).tobytes()
    db.execute_query("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, ?, ?, ?)", (event_id, "2025-06-12T12:00:00Z", arr1, len(arr1)))
    db.execute_query("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, ?, ?, ?)", (event_id, "2025-06-12T12:00:01Z", arr2, len(arr2)))
    client = TestClient(app)
    resp = client.get(f"/api/v1/events/{event_id}/frames/blobs")
    assert resp.status_code == 200
    frames = resp.json()
    assert isinstance(frames, list) and len(frames) == 2
    for f in frames:
        assert "frame" in f and "timestamp" in f and "frame_size" in f
        import base64
        blob = base64.b64decode(f["frame"])
        assert len(blob) == 32*24*4  # float32
