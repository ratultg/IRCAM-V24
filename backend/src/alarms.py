"""
alarms.py

Alarm management for IR Thermal Monitoring System.
"""
import logging
from typing import List, Dict, Optional
import sqlite3
from .database import Database
import smtplib
from email.message import EmailMessage
import json
import os

class AlarmEvent:
    """
    Represents an alarm event (zone, temperature, timestamp, type).
    """
    def __init__(self, alarm_id: int, zone_id: int, temperature: float, timestamp: str, event_type: str, acknowledged: bool = False, acknowledged_at: Optional[str] = None) -> None:
        self.alarm_id: int = alarm_id
        self.zone_id: int = zone_id
        self.temperature: float = temperature
        self.timestamp: str = timestamp
        self.event_type: str = event_type
        self.acknowledged: bool = acknowledged
        self.acknowledged_at: Optional[str] = acknowledged_at

class AlarmManager:
    """
    Manages alarm configurations, checks, and event logging, now persistent.
    """
    def __init__(self, db: Database) -> None:
        self.db = db
        self.alarms: Dict[int, Dict] = {}
        self.events: List[AlarmEvent] = []
        self.load_alarms_from_db()

    def load_alarms_from_db(self) -> None:
        self.alarms.clear()
        cur = self.db.execute_query("SELECT id, zone_id, threshold, enabled, cooldown_period, last_triggered, acknowledged, acknowledged_at FROM alarms")
        for row in cur.fetchall():
            alarm_id, zone_id, threshold, enabled, cooldown, last_triggered, acknowledged, acknowledged_at = row
            self.alarms[alarm_id] = {
                "zone_id": zone_id,
                "threshold": threshold,
                "enabled": bool(enabled),
                "cooldown_period": cooldown,
                "last_triggered": last_triggered,
                "acknowledged": bool(acknowledged),
                "acknowledged_at": acknowledged_at
            }

    def add_alarm(self, alarm_id: int, zone_id: int, threshold: float, enabled: bool = True, cooldown_period: int = 600) -> None:
        self.db.execute_query(
            "INSERT OR REPLACE INTO alarms (id, zone_id, threshold, enabled, cooldown_period) VALUES (?, ?, ?, ?, ?)",
            (alarm_id, zone_id, threshold, int(enabled), cooldown_period)
        )
        self.alarms[alarm_id] = {
            "zone_id": zone_id,
            "threshold": threshold,
            "enabled": enabled,
            "cooldown_period": cooldown_period,
            "last_triggered": None,
            "acknowledged": False,
            "acknowledged_at": None
        }
        logging.info(f"Alarm {alarm_id} added for zone {zone_id}.")

    def remove_alarm(self, alarm_id: int) -> None:
        if alarm_id in self.alarms:
            self.db.execute_query("DELETE FROM alarms WHERE id = ?", (alarm_id,))
            del self.alarms[alarm_id]
            logging.info(f"Alarm {alarm_id} removed.")
        else:
            logging.warning(f"Attempted to remove non-existent alarm {alarm_id}.")

    def check_thresholds(self, zone_id: int, temperature: float, timestamp: str) -> Optional[AlarmEvent]:
        self.load_alarms_from_db()
        for alarm_id, cfg in self.alarms.items():
            if cfg["zone_id"] == zone_id and cfg["enabled"] and temperature >= cfg["threshold"]:
                # Check cooldown and acknowledge logic here as needed
                event = AlarmEvent(alarm_id, zone_id, temperature, timestamp, "threshold", cfg.get("acknowledged", False), cfg.get("acknowledged_at"))
                self.log_event(event)
                return event
        return None

    def log_event(self, event: AlarmEvent) -> None:
        self.events.append(event)
        logging.info(f"Alarm event logged: {event.__dict__}")

    def acknowledge_alarm(self, alarm_id: int) -> None:
        self.db.execute_query("UPDATE alarms SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP WHERE id = ?", (alarm_id,))
        self.load_alarms_from_db()
        logging.info(f"Alarm {alarm_id} acknowledged.")

    def notify(self, event: AlarmEvent, email: Optional[str] = None, webhook: Optional[str] = None) -> None:
        # Real email notification logic
        notifications = self.get_notifications()
        email_notifs = [n for n in notifications if n["type"] == "email" and n["enabled"]]
        for notif in email_notifs:
            try:
                config = json.loads(notif["config"])
                to_addr = config.get("to") or email
                if not to_addr:
                    logging.warning(f"No recipient for email notification: {notif}")
                    continue
                subject = config.get("subject", f"IR Alarm Event: Zone {event.zone_id}")
                body = config.get("body", f"Alarm triggered in zone {event.zone_id} at {event.timestamp}. Temperature: {event.temperature}°C.")
                # SMTP config from env or settings
                smtp_host = os.getenv("SMTP_HOST") or config.get("smtp_host")
                smtp_port = int(os.getenv("SMTP_PORT") or config.get("smtp_port", 587))
                smtp_user = os.getenv("SMTP_USER") or config.get("smtp_user")
                smtp_pass = os.getenv("SMTP_PASS") or config.get("smtp_pass")
                from_addr = os.getenv("SMTP_FROM") or config.get("from") or smtp_user
                if not all([smtp_host, smtp_port, smtp_user, smtp_pass, from_addr]):
                    logging.error("Missing SMTP configuration for email notification.")
                    continue
                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = from_addr
                msg["To"] = to_addr
                msg.set_content(body)
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                logging.info(f"Email notification sent to {to_addr} for event: {event.__dict__}")
            except Exception as e:
                logging.error(f"Failed to send email notification: {e}")
        # Webhook placeholder
        if webhook:
            logging.info(f"Sending webhook notification for event: {event.__dict__}")

    def add_notification(self, name: str, type_: str, config: str, enabled: bool = True) -> int:
        return self.db.add_notification(name, type_, config, enabled)

    def get_notifications(self) -> list[dict]:
        return self.db.get_notifications()

    def update_notification(self, notification_id: int, name: str, type_: str, config: str, enabled: bool) -> None:
        self.db.update_notification(notification_id, name, type_, config, enabled)

    def delete_notification(self, notification_id: int) -> None:
        self.db.delete_notification(notification_id)
