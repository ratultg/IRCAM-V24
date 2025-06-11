"""
monitor.py

System monitoring and health checks for IR Thermal Monitoring System.
"""
import logging
from backend.src.sensor import ThermalSensor
from backend.src.database import Database
from backend.src.frames import ThermalFrameBuffer
from backend.src.alarms import AlarmManager

class SystemMonitor:
    """
    Aggregates health checks for sensor, database, frame buffer, and alarms.
    """
    def __init__(self, sensor: ThermalSensor, db: Database, frame_buffer: ThermalFrameBuffer, alarms: AlarmManager):
        self.sensor = sensor
        self.db = db
        self.frame_buffer = frame_buffer
        self.alarms = alarms

    def check_sensor_health(self) -> bool:
        try:
            frame = self.sensor.read_frame()
            healthy = isinstance(frame, list) and len(frame) == 768
            logging.info(f"Sensor health: {'OK' if healthy else 'FAIL'}.")
            return healthy
        except Exception as e:
            logging.error(f"Sensor health check failed: {e}")
            return False

    def check_database_health(self) -> bool:
        try:
            self.db.connect()
            self.db.conn.execute("SELECT 1;")
            logging.info("Database health: OK.")
            return True
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return False
        finally:
            self.db.close()

    def check_frame_buffer_health(self) -> bool:
        try:
            size = len(self.frame_buffer.get_all())
            logging.info(f"Frame buffer health: {size} frames in buffer.")
            return True
        except Exception as e:
            logging.error(f"Frame buffer health check failed: {e}")
            return False

    def check_alarm_system_health(self) -> bool:
        try:
            count = len(self.alarms.alarms)
            logging.info(f"Alarm system health: {count} alarms configured.")
            return True
        except Exception as e:
            logging.error(f"Alarm system health check failed: {e}")
            return False

    def health_report(self) -> dict:
        return {
            "sensor": self.check_sensor_health(),
            "database": self.check_database_health(),
            "frame_buffer": self.check_frame_buffer_health(),
            "alarms": self.check_alarm_system_health(),
        }
