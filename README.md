# IR Thermal Monitoring System Backend

## Scope of the Project

This backend provides a robust, production-grade solution for real-time IR thermal monitoring using a Raspberry Pi 5 and MLX90640 sensor. The system is designed for reliability, maintainability, and extensibility, following strict coding standards (KISS, SOLID, error handling, and test coverage). Key features include:

- **Sensor Handling**: Reliable acquisition of thermal frames from the MLX90640 sensor with error handling and retry logic.
- **Database Layer**: Efficient, transactional storage of frames, events, and configuration using SQLite with WAL and PRAGMA optimizations.
- **Zone Management**: Support for up to two user-defined rectangular zones, with CRUD operations and real-time average temperature calculations.
- **Event-Triggered Frame Storage**: Thread-safe circular buffer for continuous frame capture and event-based persistence of pre/post frames.
- **Alarm System**: Configurable alarms for temperature thresholds, event logging, and notification stubs (email/webhook ready).
- **API Endpoints**: FastAPI-based REST API for real-time data, zone management, health checks, and more.
- **System Monitoring**: Health checks for all subsystems (sensor, database, buffer, alarms) with structured logging.
- **Testing**: Comprehensive unit and integration tests, with ≥85% coverage and hardware abstraction for CI.
- **Documentation & Reference**: Living reference and implementation checklist maintained alongside the codebase.

This project is suitable for industrial, research, or educational deployments requiring reliable IR thermal monitoring, event detection, and system health assurance.

---

## Features
- **Thermal Sensor Integration**: MLX90640 via I²C, robust error handling
- **Database**: SQLite with WAL, transaction safety, and schema management
- **Zone Management**: Up to 2 rectangular zones, CRUD, and average temperature calculation
- **Event-Triggered Frame Storage**: Thread-safe buffer, event-based DB persistence
- **Alarm System**: Threshold checks, event logging, notification stubs
- **API**: FastAPI endpoints for real-time data, zones, health, and more
- **System Monitoring**: Health checks for all subsystems
- **Full Test Coverage**: Unit and integration tests for all modules

---

## Setup

### 1. Clone & Install
```sh
git clone <your-repo-url>
cd IRCAM V24
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root (see `.env.example` if present) with settings for frame buffer, event durations, FPS, and notification stubs.

### 3. Run the Backend
```sh
uvicorn backend.src.main:app --reload
```

### 4. Development: Use Mock Sensor
To run the backend with a mock sensor (random temperature data, no hardware required), set the environment variable `MOCK_SENSOR=1` before starting the server:

**PowerShell (Windows):**
```powershell
$env:MOCK_SENSOR=1
uvicorn backend.src.main:app --reload
```

**Command Prompt (Windows):**
```cmd
set MOCK_SENSOR=1
uvicorn backend.src.main:app --reload
```

**Linux/macOS (bash):**
```bash
export MOCK_SENSOR=1
uvicorn backend.src.main:app --reload
```

This is useful for development, testing, or demo purposes on any machine.

---

## API Documentation

All endpoints are under `/api/v1/`.

### Real-Time Frame
- `GET /api/v1/thermal/real-time`
  - Returns: Latest 768-value frame from the sensor

### Zones
- `GET /api/v1/zones` — List all zones
- `POST /api/v1/zones` — Create a zone
- `DELETE /api/v1/zones/{zone_id}` — Remove a zone
- `GET /api/v1/zones/{zone_id}/average` — Get average temperature for a zone

#### Example: Get Real-Time Frame
```sh
curl http://localhost:8000/api/v1/thermal/real-time
```

#### Example: Add a Zone
```sh
curl -X POST http://localhost:8000/api/v1/zones -H "Content-Type: application/json" -d '{"x1":10,"y1":10,"x2":20,"y2":20}'
```

## Zones API

### Create a Zone
POST /api/v1/zones

Request JSON:
```json
{
  "id": 1,
  "x": 0,
  "y": 0,
  "width": 2,
  "height": 2,
  "name": "My Zone",
  "color": "#00FF00"
}
```

Response JSON:
```json
{
  "id": 1,
  "x": 0,
  "y": 0,
  "width": 2,
  "height": 2,
  "name": "My Zone",
  "color": "#00FF00"
}
```

### List Zones
GET /api/v1/zones

Response JSON:
```json
[
  {
    "id": 1,
    "x": 0,
    "y": 0,
    "width": 2,
    "height": 2,
    "name": "My Zone",
    "color": "#00FF00"
  }
]
```

### Health
- `GET /api/v1/health` — System health report

---

## Testing & CI
- Run all tests:
  ```sh
  pytest --cov=backend/src
  ```
- Lint, format, and type-check:
  ```sh
  flake8 backend/src
  black --check backend/src
  mypy backend/src
  ```
- All tests must pass and coverage must be ≥85% before merging.

---

## Security & Configuration
- No hardcoded credentials: use environment variables or secure storage
- All inputs are validated and type-checked
- Logging at appropriate levels (INFO, WARNING, ERROR)

---

## Reference & Documentation
- See `copilot_py_reference.md` for a living reference of all modules/classes
- See `implementation_checklist.md` for project progress

---

## License
MIT (or your license here)
