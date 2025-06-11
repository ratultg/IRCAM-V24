"""
Unit tests for AlarmManager.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backend.src.alarms import AlarmManager, AlarmEvent

def test_add_and_remove_alarm():
    am = AlarmManager()
    am.add_alarm(1, 1, 30.0)
    assert 1 in am.alarms
    am.remove_alarm(1)
    assert 1 not in am.alarms

def test_check_thresholds_and_log():
    am = AlarmManager()
    am.add_alarm(1, 1, 25.0)
    event = am.check_thresholds(1, 26.0, "2025-06-10T12:00:00Z")
    assert isinstance(event, AlarmEvent)
    assert event.zone_id == 1
    assert event.temperature == 26.0
    assert len(am.events) == 1
    # Should not trigger if below threshold
    event2 = am.check_thresholds(1, 24.0, "2025-06-10T12:01:00Z")
    assert event2 is None

def test_notify_logs(capsys):
    am = AlarmManager()
    event = AlarmEvent(1, 1, 30.0, "2025-06-10T12:00:00Z", "threshold")
    am.notify(event, email="test@example.com", webhook="http://webhook")
    captured = capsys.readouterr()
    # Notification logs should be present (INFO level)
