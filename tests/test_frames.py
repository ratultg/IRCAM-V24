"""
Unit tests for ThermalFrameBuffer and EventTriggeredStorage.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backend.src.frames import ThermalFrameBuffer, EventTriggeredStorage

class DummyDB:
    def __init__(self):
        self.persisted = []
    def transaction(self):
        from contextlib import contextmanager
        @contextmanager
        def _tx():
            yield self
        return _tx()
    def execute_query(self, query: str, params: tuple = ()):  # Add default param
        self.persisted.append(params)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

import datetime

def test_buffer_append_and_get():
    buf = ThermalFrameBuffer(3)
    now = datetime.datetime.utcnow().isoformat()
    buf.append([1.0]*768, now)
    buf.append([2.0]*768, now)
    buf.append([3.0]*768, now)
    assert len(buf.get_all()) == 3
    buf.append([4.0]*768, now)
    assert len(buf.get_all()) == 3  # oldest evicted
    buf.clear()
    assert len(buf.get_all()) == 0

def test_event_triggered_storage():
    buf = ThermalFrameBuffer(2)
    db = DummyDB()
    storage = EventTriggeredStorage(buf, db, post_event_frames=2)
    now = datetime.datetime.utcnow().isoformat()
    # Fill buffer
    buf.append([1.0]*768, now)
    buf.append([2.0]*768, now)
    # Trigger event
    storage.trigger_event()
    # Should persist pre-event frames
    assert len(db.persisted) == 2
    # Record post-event frames
    storage.record_frame([3.0]*768, now)
    storage.record_frame([4.0]*768, now)
    # After post_event_frames, buffer should be cleared
    assert not storage._event_active
    assert len(db.persisted) == 4

def test_event_frames_api(tmp_path):
    # Integration test: insert frames, then fetch via API endpoints
    import sqlite3
    import numpy as np
    from fastapi.testclient import TestClient
    import tempfile
    from backend.src.database import Database
    from backend.src.main import app, get_db
    # Use a temp DB and re-init schema for isolation
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        # Insert a zone so that zone_id=1 is valid for event/frames
        db.execute_query("INSERT INTO zones (id, name, color) VALUES (?, ?, ?)", (1, 'Test Zone', '#00FF00'))
        # Override FastAPI dependency
        app.dependency_overrides[get_db] = lambda: db
        client = TestClient(app)
        event_id = 123
        db.execute_query("INSERT INTO alarm_events (id, zone_id, timestamp, temperature, alarm_id) VALUES (?, ?, ?, ?, ?)", (event_id, 1, "2025-06-12T12:00:00Z", 42.0, 1))
        for i in range(2):
            arr = (np.ones((24,32), dtype=np.float32) * (i+1)).tobytes()
            db.execute_query("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, ?, ?, ?)", (event_id, f"2025-06-12T12:00:0{i}Z", arr, len(arr)))
        resp = client.get(f"/api/v1/events/{event_id}/frames")
        assert resp.status_code == 200
        frames = resp.json()
        assert len(frames) == 2
        assert frames[0]["event_id"] == event_id
        resp = client.get(f"/api/v1/events/{event_id}/frames.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)
        app.dependency_overrides.pop(get_db, None)

def test_compute_heatmap_trend_anomalies():
    from backend.src.frames import compute_heatmap, compute_trend, detect_anomalies
    # Simulate 10 data points
    data = [{"timestamp": f"2025-06-12T12:00:0{i}Z", "temperature": 20.0 + i, "zone_id": 1} for i in range(10)]
    # Heatmap
    heatmap = compute_heatmap(data, 32, 24)
    assert len(heatmap) == 24 and len(heatmap[0]) == 32
    # Trend
    ts, vals = compute_trend(data)
    assert len(ts) == 10 and len(vals) == 10
    # Anomalies (none expected)
    anomalies = detect_anomalies(data)
    assert isinstance(anomalies, list)
    # Add an outlier
    data.append({"timestamp": "2025-06-12T12:00:10Z", "temperature": 100.0, "zone_id": 1})
    anomalies = detect_anomalies(data)
    assert any(a["temperature"] == 100.0 for a in anomalies)
