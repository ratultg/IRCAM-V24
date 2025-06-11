# Copilot Python File Reference

This file is maintained as a reference for all Python modules created in this project. It lists each file, its classes, methods/functions, and a brief description of its purpose and usage. Update this file as new modules are added or changed.

---

## backend/src/sensor.py
- **Class:** `ThermalSensor`
  - **__init__(self, bus=1, address=0x33, max_retries=3, backoff_factor=0.5)`**
    - Initializes the MLX90640 sensor using Adafruit driver on Raspberry Pi I2C (pins SCL=3, SDA=2).
    - Handles dependency checks, error handling, and sets refresh rate.
  - **read_frame(self) -> List[float]**
    - Reads a 768-point thermal frame from the sensor with retry and error handling.
    - Returns a list of floats (temperatures in °C).

**How the file works:**
- Provides a robust, production-safe interface to the MLX90640 sensor.
- Handles all I2C and hardware errors, logs failures, and enforces coding rules.

---

## backend/src/database.py
- **Class:** `Database`
  - **__init__(self, db_path="ir_monitoring.db")**
    - Sets up the database path and connection placeholder.
  - **connect(self)**
    - Opens a SQLite3 connection and applies PRAGMA settings for performance and safety.
  - **initialize_schema(self)**
    - Creates all required tables and indexes for the IR Thermal Monitoring System.
  - **transaction(self)**
    - Context manager for safe transactions with rollback on error.
  - **execute_query(self, query: str, params: tuple = ()) -> Any**
    - Executes a SQL query and returns the cursor.
  - **close(self)**
    - Closes the database connection and logs the action.

**How the file works:**
- Provides a safe, reusable interface for all database operations.
- Ensures schema is always up to date and transactions are safe.

---

## backend/src/frames.py
- **Class:** `ThermalFrameBuffer`
  - `__init__(self, capacity: int)`
    - Initializes a fixed-size circular buffer for thermal frames.
  - `append(self, frame: list, timestamp: str)`
    - Adds a frame with timestamp to the buffer, evicting oldest if full.
  - `get_all(self) -> list`
    - Returns all frames in the buffer in order.
  - `clear(self)`
    - Empties the buffer.

- **Class:** `EventTriggeredStorage`
  - `__init__(self, buffer: ThermalFrameBuffer, db: Database, post_event_frames: int)`
    - Coordinates event-triggered storage using the buffer and database.
  - `record_frame(self, frame: list, timestamp: str)`
    - Always appends to buffer.
  - `trigger_event(self)`
    - Persists pre-event buffer and post-event frames to DB.

**How the file works:**
- Provides memory-efficient, event-triggered storage for thermal frames.
- Used to minimize disk I/O and maximize retention around alarm events.

---

## backend/src/main.py
- **Function:** `get_sensor()`
  - Returns a singleton instance of `ThermalSensor` (enables test patching).

- **API Endpoints:**
  - `/api/v1/thermal/real-time` (GET): Returns latest frame.
  - `/api/v1/zones` (GET/POST/DELETE): CRUD for zones.
  - `/api/v1/zones/{zone_id}/average` (GET): Returns zone average.
  - `/api/v1/health` (GET): Health check.

**How the file works:**
- Entry point for the backend API server.
- Uses dependency injection for sensor to enable testability.

---

## tests/test_api.py
- **Tests:**
  - `test_health`, `test_zone_crud`, `test_real_time_frame`: Validate API endpoints, schemas, and error handling.
  - Uses fixture to patch sensor for hardware-free testing.

**How the file works:**
- Ensures API endpoints are correct and robust, independent of hardware.

---

## tests/test_sensor.py
- **Tests:**
  - `test_read_frame_success`: Verifies normal frame read.
  - `test_read_frame_retry`: Verifies retry logic on transient errors.
  - `test_read_frame_fail`: Verifies error raised after max retries.

**How the file works:**
- Uses monkeypatching to mock hardware dependencies and simulate sensor behavior.

---

## tests/test_database.py
- **Tests:**
  - `test_database_connect_and_schema`: Verifies DB connection and schema creation.
  - `test_database_crud`: Verifies basic CRUD operations on the schema.

**How the file works:**
- Uses temporary files for isolated, repeatable DB tests.

---

## backend/src/zones.py
- **Class:** `Zone`
  - `__init__(self, zone_id, x, y, width, height)`
    - Represents a rectangular zone in the thermal image.
- **Class:** `ZonesManager`
  - `add_zone(self, zone_id, x, y, width, height)`
    - Adds a new zone (max 2 zones enforced).
  - `remove_zone(self, zone_id)`
    - Removes a zone by ID.
  - `get_zones(self)`
    - Returns a list of all zones.
  - `compute_zone_average(self, zone_id, frame)`
    - Computes the average temperature for a zone from a 768-point frame.

**How the file works:**
- Provides in-memory CRUD and average calculation for up to 2 rectangular zones.
- Enforces all preconditions and logs errors as per coding rules.

---

## backend/src/alarms.py
- **Class:** `AlarmEvent`
  - `__init__(self, alarm_id, zone_id, temperature, timestamp, event_type)`
    - Represents an alarm event (zone, temperature, timestamp, type).
- **Class:** `AlarmManager`
  - `add_alarm(self, alarm_id, zone_id, threshold, enabled=True)`
    - Adds a new alarm configuration.
  - `remove_alarm(self, alarm_id)`
    - Removes an alarm by ID.
  - `check_thresholds(self, zone_id, temperature, timestamp)`
    - Checks if a zone's temperature exceeds any enabled alarm threshold, logs event if so.
  - `log_event(self, event)`
    - Appends event to the event log.
  - `notify(self, event, email=None, webhook=None)`
    - Logs notification intent (stub for real notification).

**How the file works:**
- Manages alarm configs, checks, event logging, and notification stubs.
- Designed to integrate with event-triggered storage and API.

---

## tests/test_alarms.py
- **Tests:**
  - `test_add_and_remove_alarm`: Verifies alarm CRUD.
  - `test_check_thresholds_and_log`: Verifies threshold logic and event logging.
  - `test_notify_logs`: Verifies notification logging.

**How the file works:**
- Ensures alarm logic, event logging, and notification stubs work as intended.

---

## backend/src/monitor.py
- **Class:** `SystemMonitor`
  - `__init__(self, sensor, db, frame_buffer, alarms)`
    - Aggregates health checks for all system components.
  - `check_sensor_health(self) -> bool`
    - Checks if the sensor is healthy (can read a valid frame).
  - `check_database_health(self) -> bool`
    - Checks if the database is accessible and operational.
  - `check_frame_buffer_health(self) -> bool`
    - Checks if the frame buffer is accessible.
  - `check_alarm_system_health(self) -> bool`
    - Checks if the alarm system is configured.
  - `health_report(self) -> dict`
    - Returns a dict with the health status of all components.

**How the file works:**
- Provides a unified health check interface for the system.
- Used for diagnostics and API health endpoints.

---

## tests/test_monitor.py
- **Tests:**
  - `test_health_report_all_ok`: All components healthy.
  - `test_sensor_fail`: Sensor health check fails.
  - `test_db_fail`: Database health check fails.

**How the file works:**
- Ensures system health checks and reporting are robust and correct.

---

(Keep this file updated as you add new modules, classes, or major functions.)
