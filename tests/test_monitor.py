"""
Unit tests for SystemMonitor.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backend.src.monitor import SystemMonitor

class DummySensor:
    def read_frame(self):
        return [0.0] * 768
class DummyDB:
    def connect(self): pass
    def close(self): pass
    @property
    def conn(self):
        class Conn:
            def execute(self, q): return None
        return Conn()
class DummyFrameBuffer:
    def get_all(self): return [[0.0]*768]
class DummyAlarms:
    alarms = {1: {}}

def test_health_report_all_ok():
    monitor = SystemMonitor(DummySensor(), DummyDB(), DummyFrameBuffer(), DummyAlarms())
    report = monitor.health_report()
    assert report == {"sensor": True, "database": True, "frame_buffer": True, "alarms": True}

def test_sensor_fail():
    class FailingSensor:
        def read_frame(self): raise Exception("fail")
    monitor = SystemMonitor(FailingSensor(), DummyDB(), DummyFrameBuffer(), DummyAlarms())
    assert not monitor.check_sensor_health()

def test_db_fail():
    class FailingDB(DummyDB):
        @property
        def conn(self):
            raise RuntimeError("DB connection failed")
        def connect(self): raise RuntimeError("fail")
    monitor = SystemMonitor(DummySensor(), FailingDB(), DummyFrameBuffer(), DummyAlarms())
    assert not monitor.check_database_health()
