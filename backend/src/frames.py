"""
frames.py

Event-triggered frame storage for IR Thermal Monitoring System.
"""
import threading
from collections import deque
from typing import List, Tuple, Protocol, runtime_checkable, Any
import logging
from types import TracebackType

class ThermalFrameBuffer:
    """
    Circular buffer for pre-alarm frame storage in memory.
    Thread-safe for concurrent access.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: deque[Tuple[str, List[float]]] = deque(maxlen=capacity)
        self.lock = threading.Lock()

    def append(self, frame: List[float], timestamp: str) -> None:
        with self.lock:
            self.buffer.append((timestamp, frame.copy()))
            logging.debug("Frame appended at %s. Buffer size: %d", timestamp, len(self.buffer))

    def get_all(self) -> List[Tuple[str, List[float]]]:
        with self.lock:
            return list(self.buffer)

    def clear(self) -> None:
        with self.lock:
            self.buffer.clear()
            logging.info("ThermalFrameBuffer cleared.")

    def __len__(self) -> int:
        with self.lock:
            return len(self.buffer)

@runtime_checkable
class DBProtocol(Protocol):
    def transaction(self) -> Any: ...
    def execute_query(self, query: str, params: tuple = ...) -> object: ...
    def __enter__(self) -> Any: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None: ...

class EventTriggeredStorage:
    """
    Main storage coordinator for alarm events.
    Persists pre-event buffer and post-event frames to DB.
    """
    def __init__(self, buffer: ThermalFrameBuffer, db: DBProtocol, post_event_frames: int = 20) -> None:
        self.buffer = buffer
        self.db = db
        self.post_event_frames = post_event_frames
        self._post_event_count = 0
        self._event_active = False
        self._lock = threading.Lock()

    def record_frame(self, frame: list[float], timestamp: str) -> None:
        self.buffer.append(frame, timestamp)
        with self._lock:
            if self._event_active:
                self._post_event_count -= 1
                self._persist_frame(frame, timestamp)
                if self._post_event_count <= 0:
                    self._event_active = False
                    self.buffer.clear()
            logging.debug("Frame appended at %s. Buffer size: %d", timestamp, len(self.buffer))

    def trigger_event(self) -> None:
        with self._lock:
            if self._event_active:
                logging.warning("Event already active; ignoring trigger.")
                return
            # Persist pre-event frames
            for ts, frame in self.buffer.get_all():
                self._persist_frame(frame, ts)
            self._event_active = True
            self._post_event_count = self.post_event_frames
            logging.info("Event triggered: persisting %d pre-event frames and %d post-event frames.", len(self.buffer.get_all()), self.post_event_frames)

    def _persist_frame(self, frame: list[float], timestamp: str) -> None:
        try:
            with self.db.transaction():
                self.db.execute_query(
                    "INSERT INTO thermal_frames (timestamp, frame, frame_size) VALUES (?, ?, ?)",
                    (timestamp, self._serialize_frame(frame), len(frame)),
                )
            logging.debug("Frame persisted at %s.", timestamp)
        except (AttributeError, RuntimeError, ValueError) as exc:
            logging.error("Failed to persist frame: %s", exc)

    @staticmethod
    def _serialize_frame(frame: list[float]) -> bytes:
        import struct
        return struct.pack(f"{len(frame)}f", *frame)
