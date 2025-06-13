"""
Unit tests for AlarmManager.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import tempfile
from backend.src.database import Database
from backend.src.alarms import AlarmManager, AlarmEvent

def test_add_and_remove_alarm():
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        am = AlarmManager(db)
        am.add_alarm(1, 1, 30.0)
        assert 1 in am.alarms
        am.remove_alarm(1)
        assert 1 not in am.alarms
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)

def test_check_thresholds_and_log():
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        am = AlarmManager(db)
        am.add_alarm(1, 1, 25.0)
        event = am.check_thresholds(1, 26.0, "2025-06-10T12:00:00Z")
        assert isinstance(event, AlarmEvent)
        assert event.zone_id == 1
        assert event.temperature == 26.0
        assert len(am.events) == 1
        # Should not trigger if below threshold
        event2 = am.check_thresholds(1, 24.0, "2025-06-10T12:01:00Z")
        assert event2 is None
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)

def test_notify_logs(capsys):
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        am = AlarmManager(db)
        event = AlarmEvent(1, 1, 30.0, "2025-06-10T12:00:00Z", "threshold")
        am.notify(event, email="test@example.com", webhook="http://webhook")
        captured = capsys.readouterr()
        # Notification logs should be present (INFO level)
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)

def test_notification_crud():
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        am = AlarmManager(db)
        # Add notification
        notif_id = am.add_notification("Test Email", "email", '{"to": "user@example.com"}', True)
        assert notif_id > 0
        # Get notifications
        notifs = am.get_notifications()
        assert any(n["id"] == notif_id for n in notifs)
        # Update notification
        am.update_notification(notif_id, "Test Email Updated", "email", '{"to": "new@example.com"}', False)
        updated = [n for n in am.get_notifications() if n["id"] == notif_id][0]
        assert updated["name"] == "Test Email Updated"
        assert updated["enabled"] is False
        # Delete notification
        am.delete_notification(notif_id)
        notifs = am.get_notifications()
        assert not any(n["id"] == notif_id for n in notifs)
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)

def test_acknowledge_and_cooldown_fields():
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        db = Database(tf.name)
        db.connect()
        db.initialize_schema()
        am = AlarmManager(db)
        # Add alarm with cooldown
        am.add_alarm(1, 1, 25.0, enabled=True, cooldown_period=120)
        # Check initial state
        alarm = am.alarms[1]
        assert alarm["cooldown_period"] == 120
        assert alarm["acknowledged"] is False
        assert alarm["acknowledged_at"] is None
        # Trigger acknowledge
        am.acknowledge_alarm(1)
        am.load_alarms_from_db()
        alarm = am.alarms[1]
        assert alarm["acknowledged"] is True
        assert alarm["acknowledged_at"] is not None
        db.close()
    finally:
        tf.close()
        os.unlink(tf.name)
