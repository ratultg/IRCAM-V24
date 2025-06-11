# Implementation Checklist

_This checklist tracks each step of the IR Thermal Monitoring System implementation. Mark each item `[x]` once it’s completed and tested._

---
## ▶ General Requirements (all phases)
- [ ] Follow KISS, YAGNI & SOLID principles
- [ ] Add concise docstrings to every module, class and function
- [ ] Validate preconditions before critical operations
- [ ] Implement structured error handling with clear failure modes
- [ ] Sanitize and type-check all inputs
- [ ] No hardcoded credentials; use secure storage
- [ ] Log actions at appropriate levels (`INFO`, `WARNING`, `ERROR`)
- [ ] Write unit & integration tests for new logic (≥85% coverage)
- [ ] Ensure CI pipeline runs lint, format and tests on every push

---
## Phase 0 – Project & Environment Setup
- [ ] Create branch `feature/00-project-setup`
- [ ] Initialize `.venv` and install dev dependencies
- [ ] Scaffold `backend/src/` modules:
  - `main.py`, `sensor.py`, `database.py`, `zones.py`, `alarms.py`, `frames.py`, `monitor.py`
- [ ] Add module-level docstrings and type stubs
- [ ] Configure CI for linting and tests
- [ ] Run `flake8`, `black`, `mypy` with zero errors

---
## Phase 1 – Sensor Layer
- [x] Implement `ThermalSensor` in `sensor.py`
  - `read_frame() -> List[float]` with 768 values
  - I²C precondition and retry logic
- [x] Write `tests/test_sensor.py` covering:
  - Mock I²C reads
  - Frame length and data types
  - Timeout and error paths
- [x] Add `check_sensor_health() -> bool` in `monitor.py`
- [x] Verify health logs at correct severity

---
## Phase 2 – Data Layer
- [x] Create `Database` class in `database.py`
  - `connect()`, `initialize_schema()`, `execute_query()`, `close()`
  - Apply PRAGMA settings: WAL, cache, temp_store, synchronous
- [x] Add transaction context manager with rollback
- [x] Write `tests/test_database.py`:
  - Temporary SQLite file
  - Schema creation and CRUD operations

---
## Phase 3 – Zone Management
- [x] Build `ZonesManager` in `zones.py`
  - `add_zone()`, `remove_zone()`, `get_zones()`, `compute_zone_average()`
  - Enforce max 2 zones
- [x] Write `tests/test_zones.py`:
  - CRUD and average calculations
- [x] Log precondition failures and errors

---
## Phase 4 – API Endpoints
- [x] Configure FastAPI in `main.py` under `/api/v1/`
- [x] Define Pydantic request/response models
- [x] Implement endpoints:
  - `GET /thermal/real-time`
  - CRUD on `/zones`
  - `GET /zones/{zone_id}/average`
  - `GET /health`
- [x] Write `tests/test_api.py` using FastAPI `TestClient`
- [x] Validate status codes, payload schemas and error responses

---
## Phase 5 – Event-Triggered Frame Storage
- [x] Implement `ThermalFrameBuffer` in `frames.py`
- [x] Develop `EventTriggeredStorage`:
  - Buffer frames continuously
  - On `trigger_event()`, persist pre/post frames to DB
- [x] Add configuration via `.env` for durations/FPS
- [x] Write `tests/test_frames.py` for buffer and persistence flows

---
## Phase 6 – Alarm System
- [x] Implement `AlarmManager` in `alarms.py`
  - `check_thresholds()`, `log_event()`, `notify()`
  - Hook into `EventTriggeredStorage`
- [x] Support email and webhook notifications via secure config (stubbed)
- [x] Write `tests/test_alarms.py` for threshold, logging, notify mocks

---
## Phase 7 – System Monitoring & Health
- [x] Add health-check functions in `monitor.py`
- [x] Write `tests/test_monitor.py` for each check

---
## Phase 8 – Integration & Release
- [x] Create end-to-end tests in `tests/test_integration.py`
- [x] Update `README.md` with setup, API docs, examples
- [ ] Conduct security review: no hardcoded creds, validate inputs
- [ ] Run full CI: lint, format, tests, coverage ≥85%
- [ ] Merge to `main`, tag release, document rollback plan