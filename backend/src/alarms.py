"""
alarms.py

Alarm management for IR Thermal Monitoring System.
"""
import logging
from typing import List, Dict, Optional

class AlarmEvent:
    """
    Represents an alarm event (zone, temperature, timestamp, type).
    """
    def __init__(self, alarm_id: int, zone_id: int, temperature: float, timestamp: str, event_type: str):
        self.alarm_id = alarm_id
        self.zone_id = zone_id
        self.temperature = temperature
        self.timestamp = timestamp
        self.event_type = event_type

class AlarmManager:
    """
    Manages alarm configurations, checks, and event logging.
    """
    def __init__(self):
        self.alarms: Dict[int, Dict] = {}  # alarm_id -> config dict
        self.events: List[AlarmEvent] = []

    def add_alarm(self, alarm_id: int, zone_id: int, threshold: float, enabled: bool = True):
        self.alarms[alarm_id] = {"zone_id": zone_id, "threshold": threshold, "enabled": enabled}
        logging.info(f"Alarm {alarm_id} added for zone {zone_id}.")

    def remove_alarm(self, alarm_id: int):
        if alarm_id in self.alarms:
            del self.alarms[alarm_id]
            logging.info(f"Alarm {alarm_id} removed.")
        else:
            logging.warning(f"Attempted to remove non-existent alarm {alarm_id}.")

    def check_thresholds(self, zone_id: int, temperature: float, timestamp: str) -> Optional[AlarmEvent]:
        for alarm_id, cfg in self.alarms.items():
            if cfg["zone_id"] == zone_id and cfg["enabled"] and temperature >= cfg["threshold"]:
                event = AlarmEvent(alarm_id, zone_id, temperature, timestamp, "threshold")
                self.log_event(event)
                return event
        return None

    def log_event(self, event: AlarmEvent):
        self.events.append(event)
        logging.info(f"Alarm event logged: {event.__dict__}")

    def notify(self, event: AlarmEvent, email: Optional[str] = None, webhook: Optional[str] = None):
        # Placeholder for notification logic
        if email:
            logging.info(f"Sending email notification for event: {event.__dict__}")
        if webhook:
            logging.info(f"Sending webhook notification for event: {event.__dict__}")
