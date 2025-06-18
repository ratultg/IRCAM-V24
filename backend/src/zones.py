"""
zones.py

Zone management for IR Thermal Monitoring System.
"""
import logging
from typing import List, Dict, Optional
import sqlite3
from .database import Database

class Zone:
    """
    Represents a single rectangular area on the image, with optional name, color, enabled, and threshold.
    """
    def __init__(self, zone_id: int, x: int, y: int, width: int, height: int, name: str | None = None, color: str | None = None, enabled: bool = True, threshold: float | None = None) -> None:
        self.id: int = zone_id
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.name: str = name or f"Zone ({x},{y})"
        self.color: str = color or "#FF0000"  # Default to red
        self.enabled: bool = enabled
        self.threshold: float | None = threshold

class ZonesManager:
    """
    Manages up to 2 zones, provides CRUD and average calculation, now persistent.
    """
    def __init__(self, db: Database) -> None:
        self.db = db
        self.zones: dict[int, Zone] = {}
        self.load_zones_from_db()

    def load_zones_from_db(self) -> None:
        try:
            self.zones.clear()
            cur = self.db.execute_query("SELECT id, x, y, width, height, name, color, enabled, threshold FROM zones")
            for row in cur.fetchall():
                zone_id, x, y, width, height, name, color, enabled, threshold = row
                self.zones[zone_id] = Zone(zone_id, x, y, width, height, name, color, bool(enabled), threshold)
            logging.info("Loaded %d zones from DB.", len(self.zones))
        except Exception as e:
            logging.error("Error loading zones from DB: %s", e, exc_info=True)
            raise

    def add_zone(self, zone_id: int, x: int, y: int, width: int, height: int, name: str | None = None, color: str | None = None, enabled: bool = True, threshold: float | None = None) -> None:
        try:
            if len(self.zones) >= 2:
                logging.error("Cannot add more than 2 zones.")
                raise ValueError("Maximum of 2 zones allowed.")
            self.db.execute_query(
                "INSERT OR REPLACE INTO zones (id, x, y, width, height, name, color, enabled, threshold) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (zone_id, x, y, width, height, name or f"Zone ({x},{y})", color or "#FF0000", int(enabled), threshold)
            )
            self.zones[zone_id] = Zone(zone_id, x, y, width, height, name, color, enabled, threshold)
            logging.info("Zone %d added with name '%s', color '%s', enabled %s, threshold %s.", zone_id, name, color, enabled, threshold)
        except Exception as e:
            logging.error("Error adding zone %d: %s", zone_id, e, exc_info=True)
            raise

    def remove_zone(self, zone_id: int) -> None:
        try:
            if zone_id not in self.zones:
                logging.error("Zone ID %d does not exist.", zone_id)
                raise ValueError("Zone ID does not exist.")
            self.db.execute_query("DELETE FROM zones WHERE id = ?", (zone_id,))
            del self.zones[zone_id]
            logging.info("Zone %d removed.", zone_id)
        except Exception as e:
            logging.error("Error removing zone %d: %s", zone_id, e, exc_info=True)
            raise

    def get_zones(self) -> list[Zone]:
        try:
            self.load_zones_from_db()
            return list(self.zones.values())
        except Exception as e:
            logging.error("Error getting zones: %s", e, exc_info=True)
            raise

    def compute_zone_average(self, zone_id: int, frame: list[float]) -> float:
        try:
            if zone_id not in self.zones:
                logging.error("Zone ID %d does not exist for average computation.", zone_id)
                raise ValueError("Zone ID does not exist.")
            zone = self.zones[zone_id]
            # MLX90640 is 32x24
            values: list[float] = []
            for row in range(zone.y, zone.y + zone.height):
                for col in range(zone.x, zone.x + zone.width):
                    idx = row * 32 + col
                    if 0 <= idx < len(frame):
                        values.append(frame[idx])
            if not values:
                logging.warning("Zone %d has no valid pixels.", zone_id)
                return 0.0
            avg: float = sum(values) / len(values)
            logging.info("Zone %d average: %.2f", zone_id, avg)
            return avg
        except Exception as e:
            logging.error("Error computing average for zone %d: %s", zone_id, e, exc_info=True)
            raise

    def update_zone(self, zone_id: int, x: int, y: int, width: int, height: int, name: str | None = None, color: str | None = None, enabled: bool = True, threshold: float | None = None) -> None:
        try:
            if zone_id not in self.zones:
                logging.error("Zone ID %d does not exist.", zone_id)
                raise ValueError("Zone ID does not exist.")
            self.db.execute_query(
                "UPDATE zones SET x=?, y=?, width=?, height=?, name=?, color=?, enabled=?, threshold=? WHERE id=?",
                (x, y, width, height, name or f"Zone ({x},{y})", color or "#FF0000", int(enabled), threshold, zone_id)
            )
            self.zones[zone_id] = Zone(zone_id, x, y, width, height, name, color, enabled, threshold)
            logging.info("Zone %d updated with name '%s', color '%s', enabled %s, threshold %s.", zone_id, name, color, enabled, threshold)
        except Exception as e:
            logging.error("Error updating zone %d: %s", zone_id, e, exc_info=True)
            raise
