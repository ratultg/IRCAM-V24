"""
database.py

Database handler for IR Thermal Monitoring System (SQLite3).
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Any, Iterator
import shutil

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
            x INTEGER NOT NULL DEFAULT 0,
            y INTEGER NOT NULL DEFAULT 0,
            width INTEGER NOT NULL DEFAULT 0,
            height INTEGER NOT NULL DEFAULT 0,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#FF0000',
            enabled BOOLEAN DEFAULT 1,           -- New: persistent enabled flag
            threshold REAL                       -- New: persistent threshold
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
            cooldown_period INTEGER DEFAULT 600,     -- New: cooldown/debounce
            last_triggered DATETIME,                 -- New: last triggered timestamp
            acknowledged BOOLEAN DEFAULT 0,          -- New: persistent acknowledge
            acknowledged_at DATETIME,                -- New: acknowledge timestamp
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,           -- 'email', 'webhook', 'sms'
            config TEXT,                  -- JSON-encoded configuration
            enabled BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT
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

    def add_notification(self, name: str, type_: str, config: str, enabled: bool = True) -> int:
        """Add a new notification config to the database."""
        assert self.conn is not None
        cur = self.conn.execute(
            "INSERT INTO notifications (name, type, config, enabled) VALUES (?, ?, ?, ?)",
            (name, type_, config, int(enabled))
        )
        self.conn.commit()
        return int(cur.lastrowid) if cur.lastrowid is not None else -1

    def get_notifications(self) -> list[dict]:
        """Retrieve all notification configs."""
        assert self.conn is not None
        cur = self.conn.execute("SELECT id, name, type, config, enabled, created_at FROM notifications")
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "config": row[3],
                "enabled": bool(row[4]),
                "created_at": row[5],
            }
            for row in cur.fetchall()
        ]

    def update_notification(self, notification_id: int, name: str, type_: str, config: str, enabled: bool) -> None:
        """Update an existing notification config."""
        assert self.conn is not None
        self.conn.execute(
            "UPDATE notifications SET name = ?, type = ?, config = ?, enabled = ? WHERE id = ?",
            (name, type_, config, int(enabled), notification_id)
        )
        self.conn.commit()

    def delete_notification(self, notification_id: int) -> None:
        """Delete a notification config."""
        assert self.conn is not None
        self.conn.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        self.conn.commit()

    def get_setting(self, key: str) -> Optional[dict]:
        """Retrieve a setting by its key."""
        assert self.conn is not None
        cur = self.conn.execute("SELECT key, value, description FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            return {"key": row[0], "value": row[1], "description": row[2]}
        return None

    def set_setting(self, key: str, value: str, description: Optional[str] = None) -> None:
        """Set a setting value, creating or updating as necessary."""
        assert self.conn is not None
        self.conn.execute(
            "INSERT INTO settings (key, value, description) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, description=excluded.description",
            (key, value, description)
        )
        self.conn.commit()

    def list_settings(self) -> list[dict]:
        """List all settings."""
        assert self.conn is not None
        cur = self.conn.execute("SELECT key, value, description FROM settings")
        return [{"key": row[0], "value": row[1], "description": row[2]} for row in cur.fetchall()]

    def delete_setting(self, key: str) -> None:
        """Delete a setting by its key."""
        assert self.conn is not None
        self.conn.execute("DELETE FROM settings WHERE key = ?", (key,))
        self.conn.commit()

    def backup(self, backup_path: str) -> None:
        """Backup the current database to the specified file."""
        assert self.conn is not None
        with open(self.db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())

    def restore(self, backup_path: str) -> None:
        assert self.conn is not None
        self.conn.close()
        import shutil
        shutil.copy2(backup_path, self.db_path)
        self.connect()

    def stream_backup(self):
        """Stream the current database file for backup purposes."""
        assert self.conn is not None
        with open(self.db_path, 'rb') as f:
            return f.read()

    def migrate(self) -> None:
        """Re-initialize the schema (idempotent, safe for upgrades)."""
        self.initialize_schema()

    def get_thermal_data(self, start_time: str, end_time: str, zone_id: int | None = None) -> list[dict]:
        """Fetch thermal_data rows for a time range and optional zone."""
        assert self.conn is not None
        if zone_id is not None:
            cur = self.conn.execute(
                "SELECT timestamp, temperature, zone_id FROM thermal_data WHERE timestamp BETWEEN ? AND ? AND zone_id = ? ORDER BY timestamp ASC",
                (start_time, end_time, zone_id)
            )
        else:
            cur = self.conn.execute(
                "SELECT timestamp, temperature, zone_id FROM thermal_data WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC",
                (start_time, end_time)
            )
        return [
            {"timestamp": row[0], "temperature": row[1], "zone_id": row[2]} for row in cur.fetchall()
        ]

    def get_zone_grid(self, zone_id: int) -> dict:
        """Fetch zone grid info (x, y, width, height) for a zone."""
        assert self.conn is not None
        cur = self.conn.execute(
            "SELECT x, y, width, height FROM zones WHERE id = ?",
            (zone_id,)
        )
        row = cur.fetchone()
        if row:
            return {"x": row[0], "y": row[1], "width": row[2], "height": row[3]}
        return {}
