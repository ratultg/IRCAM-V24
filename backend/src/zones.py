"""
zones.py

Zone management for IR Thermal Monitoring System.
"""
import logging
from typing import List, Dict, Optional

class Zone:
    """
    Represents a single rectangular area on the image, with optional name and color.
    """
    def __init__(self, zone_id: int, x: int, y: int, width: int, height: int, name: str | None = None, color: str | None = None) -> None:
        self.id: int = zone_id
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.name: str = name or f"Zone ({x},{y})"
        self.color: str = color or "#FF0000"  # Default to red

class ZonesManager:
    """
    Manages up to 2 zones, provides CRUD and average calculation.
    """
    def __init__(self) -> None:
        self.zones: dict[int, Zone] = {}

    def add_zone(self, zone_id: int, x: int, y: int, width: int, height: int, name: str | None = None, color: str | None = None) -> None:
        if len(self.zones) >= 2:
            logging.error("Cannot add more than 2 zones.")
            raise ValueError("Maximum of 2 zones allowed.")
        zone = Zone(zone_id, x, y, width, height, name, color)
        self.zones[zone_id] = zone
        logging.info("Zone %d added with name '%s' and color '%s'.", zone_id, zone.name, zone.color)

    def remove_zone(self, zone_id: int) -> None:
        if zone_id not in self.zones:
            logging.error("Zone ID %d does not exist.", zone_id)
            raise ValueError("Zone ID does not exist.")
        del self.zones[zone_id]
        logging.info("Zone %d removed.", zone_id)

    def get_zones(self) -> list[Zone]:
        return list(self.zones.values())

    def compute_zone_average(self, zone_id: int, frame: list[float]) -> float:
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
