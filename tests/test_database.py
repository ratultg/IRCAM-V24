"""
Unit tests for Database handler.
"""
import sys
import os
import tempfile
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.src.database import Database

def test_database_connect_and_schema():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        db_path = tf.name
    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    # Check tables exist
    cur = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cur.fetchall()}
    assert 'zones' in tables
    assert 'thermal_data' in tables
    assert 'alarm_events' in tables
    assert 'thermal_frames' in tables
    assert 'alarms' in tables
    db.close()
    os.remove(db_path)

def test_database_crud():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        db_path = tf.name
    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    # Insert zone
    db.execute_query("INSERT INTO zones DEFAULT VALUES")
    zone_id = db.conn.execute("SELECT id FROM zones").fetchone()[0]
    # Insert data
    db.execute_query("INSERT INTO thermal_data (zone_id, temperature) VALUES (?, ?)", (zone_id, 25.5))
    row = db.conn.execute("SELECT temperature FROM thermal_data WHERE zone_id=?", (zone_id,)).fetchone()
    assert row[0] == 25.5
    db.close()
    os.remove(db_path)
