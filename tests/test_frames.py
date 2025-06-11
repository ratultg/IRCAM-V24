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
    def execute_query(self, query, params):
        self.persisted.append(params)

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
