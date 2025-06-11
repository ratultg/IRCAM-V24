"""
frames.py

Event-triggered frame storage for IR Thermal Monitoring System.
"""
import threading
from collections import deque
from typing import List, Tuple, Optional
import logging

class ThermalFrameBuffer:
    """
    Circular buffer for pre-alarm frame storage in memory.
    Thread-safe for concurrent access.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: deque[Tuple[str, List[float]]] = deque(maxlen=capacity)
        self.lock = threading.Lock()

    def append(self, frame: List[float], timestamp: str):
        with self.lock:
            self.buffer.append((timestamp, frame.copy()))
            logging.debug(f"Frame appended at {timestamp}. Buffer size: {len(self.buffer)}")

    def get_all(self) -> List[Tuple[str, List[float]]]:
        with self.lock:
            return list(self.buffer)

    def clear(self):
        with self.lock:
            self.buffer.clear()
            logging.info("ThermalFrameBuffer cleared.")

class EventTriggeredStorage:
    """
    Main storage coordinator for alarm events.
    Persists pre-event buffer and post-event frames to DB.
    """
    def __init__(self, buffer: ThermalFrameBuffer, db, post_event_frames: int = 20):
        self.buffer = buffer
        self.db = db
        self.post_event_frames = post_event_frames
        self._post_event_count = 0
        self._event_active = False
        self._lock = threading.Lock()

    def record_frame(self, frame: List[float], timestamp: str):
        self.buffer.append(frame, timestamp)
        with self._lock:
            if self._event_active:
                self._post_event_count -= 1
                self._persist_frame(frame, timestamp)
                if self._post_event_count <= 0:
                    self._event_active = False
                    self.buffer.clear()

    def trigger_event(self):
        with self._lock:
            if self._event_active:
                logging.warning("Event already active; ignoring trigger.")
                return
            # Persist pre-event frames
            for ts, frame in self.buffer.get_all():
                self._persist_frame(frame, ts)
            self._event_active = True
            self._post_event_count = self.post_event_frames
            logging.info(f"Event triggered: persisting {len(self.buffer.get_all())} pre-event frames and {self.post_event_frames} post-event frames.")

    def _persist_frame(self, frame: List[float], timestamp: str):
        # Store frame in DB (implement as needed)
        try:
            with self.db.transaction():
                self.db.execute_query(
                    "INSERT INTO thermal_frames (timestamp, frame, frame_size) VALUES (?, ?, ?)",
                    (timestamp, self._serialize_frame(frame), len(frame)),
                )
            logging.debug(f"Frame persisted at {timestamp}.")
        except Exception as e:
            logging.error(f"Failed to persist frame: {e}")

    @staticmethod
    def _serialize_frame(frame: List[float]) -> bytes:
        import struct
        return struct.pack(f"{len(frame)}f", *frame)
