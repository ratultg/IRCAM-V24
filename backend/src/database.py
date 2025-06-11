"""
database.py

Database handler for IR Thermal Monitoring System (SQLite3).
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Any, Iterator

class Database:
    """
    Handles SQLite3 database operations for the IR Thermal Monitoring System.
    """
    def __init__(self, db_path: str = "ir_monitoring.db") -> None:
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Open a connection to the SQLite database and apply PRAGMA settings."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        assert self.conn is not None
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA cache_size=10000;")
        self.conn.execute("PRAGMA temp_store=MEMORY;")
        logging.info("Database connected and PRAGMA set.")

    def initialize_schema(self) -> None:
        """Create all required tables and indexes if they do not exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#FF0000'
        );
        CREATE TABLE IF NOT EXISTS thermal_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS alarm_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            alarm_id INTEGER,
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS thermal_frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            frame BLOB,
            frame_size INTEGER,
            FOREIGN KEY (event_id) REFERENCES alarm_events(id)
        );
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            enabled INTEGER DEFAULT 1,
            threshold REAL,
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        );
        CREATE INDEX IF NOT EXISTS idx_thermal_data_timestamp ON thermal_data(timestamp);
        CREATE INDEX IF NOT EXISTS idx_thermal_data_zone_time ON thermal_data(zone_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_thermal_frames_timestamp ON thermal_frames(timestamp);
        CREATE INDEX IF NOT EXISTS idx_thermal_frames_event ON thermal_frames(event_id);
        CREATE INDEX IF NOT EXISTS idx_alarm_events_timestamp ON alarm_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_alarm_events_alarm_id ON alarm_events(alarm_id);
        CREATE INDEX IF NOT EXISTS idx_zones_active ON zones(id);
        CREATE INDEX IF NOT EXISTS idx_alarms_enabled ON alarms(enabled);
        """
        assert self.conn is not None
        self.conn.executescript(schema)
        self.conn.commit()
        logging.info("Database schema initialized.")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager for DB transactions with rollback on failure."""
        assert self.conn is not None
        try:
            yield self.conn
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Transaction failed: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor."""
        assert self.conn is not None
        cur = self.conn.execute(query, params)
        return cur

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
