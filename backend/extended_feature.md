# IR Thermal Monitoring System: Extended Feature Set

This document aggregates the planned and desired features for the IR Thermal Monitoring System backend. It is intended as a comprehensive reference for backend development, planning, and stakeholder review.

> **⚠️ IMPORTANT STATUS NOTE**: This document contains both implemented features and planned features. 
> - **[implemented]** = Feature is working and tested
> - **[planned]** = Feature is documented but not yet implemented
> - **[basic only]** = Basic implementation exists but lacks advanced features

---

# Table of Contents
1. [Feature List](#feature-list)
2. [Implementation Checklist](#implementation-checklist)
3. [Technical Appendix](#technical-appendix)

---

# Feature Implementation Summary

| Feature/Field                | In-Memory Only | Persistent (DB) | Notes                                  |
|------------------------------|:--------------:|:---------------:|----------------------------------------|
| Zone name, color             |                |       ✓         |                                        |
| Zone enabled                 |                |       ✓         | Now persistent in DB                   |
| Zone threshold               |                |       ✓         | Now persistent in DB                   |
| Alarm threshold              |                |       ✓         |                                        |
| Alarm cooldown/acknowledge   |                |       ✓         | Now persistent in DB                   |
| Notification settings        |                |       ✓         | Now persistent in DB                   |
| Event frame storage          |                |       ✓         |                                        |

> **Persistence Recommendation:**
> Features currently marked as "In-Memory Only" (such as zone enabled/threshold, alarm cooldown/acknowledge, notification settings) should be migrated to persistent storage (database) for reliability, scalability, and production-readiness. In-memory storage is only suitable for prototyping or single-instance, non-critical deployments.

---

# Feature List

## 1. Real-Time Monitoring
**Implemented:**
- Live thermal data streaming (API)
- Real-time zone temperature display
- Live alarm status indicator

**Planned:**
- None (all core features implemented)

**Backend Changes:**
- `src/main.py`: API endpoints for live data and status.
- `src/frames.py`: Frame buffer for real-time access.
- `src/zones.py`: Per-zone temperature data.

---

## 2. Zone Management
**Implemented:**
- User-configurable zones (draw, edit, delete, name, color) (API)
- In-memory storage of zones with name and color support
- API endpoints for basic CRUD operations

**Planned:**
- Per-zone temperature thresholds (persistent; **migration from in-memory required**)
- Per-zone enable/disable (persistent; **migration from in-memory required**)

**Migration Note:**
- Current in-memory storage for zone enabled/threshold should be replaced with persistent DB fields to ensure settings survive restarts and support multi-instance deployments.

**Backend Changes / Implementation Steps:**
- [ ] Update DB schema: add `enabled`, `threshold` to `zones` table in `src/database.py` [planned]
- [ ] Write migration script to add `enabled`, `threshold` columns to existing DB [planned]
- [ ] Refactor `ZoneManager` and `ZoneDatabase` in `src/zones.py` to read/write `enabled`, `threshold` from DB [planned]
- [ ] Update CRUD API endpoints in `src/main.py` to support persistent zone attributes [planned]
- [ ] Add/extend tests for persistent zone attributes in `tests/test_zones.py` [planned]

---

## 3. Alarm System
**Implemented:**
- Per-zone alarm threshold configuration (basic)
- Alarm event logging (timestamp, zone, temperature, snapshot reference) (basic, in-memory)

**Planned:**
- Alarm state reset/acknowledge (persistent; **migration from in-memory required**)
- Alarm history retrieval (API)
- Event-triggered actions
- Advanced alarm features (cooldown, acknowledge, debounce; **migration from in-memory required**)

**Migration Note:**
- Alarm cooldown, acknowledge, and related state should be persisted in the database for reliability and auditability.

**Backend Changes / Implementation Steps:**
- [x] Update DB schema: add `cooldown_period`, `last_triggered`, `acknowledged`, `acknowledged_at` to `alarms` table in `src/database.py` [implemented]
- [x] Write migration script for alarm table changes [implemented]
- [x] Refactor `AlarmManager` and `AlarmEvent` in `src/alarms.py` to persist cooldown/acknowledge state [implemented]
- [x] Implement persistent alarm acknowledge/reset logic in API (`src/main.py`) [implemented]
- [x] Add/extend tests for persistent alarm state in `tests/test_alarms.py` [implemented]

---

## 4. Notifications
**Implemented:**
- Persistent, configurable email notifications (SMTP settings, recipients; stored in DB)
- Notification delivery on alarm events (real email via SMTP)
- Notification settings CRUD via API
- Logging and error handling for email delivery
- Logging stubs for webhook notifications

**Planned:**
- Per-zone notification enable/disable (**should be persistent**)
- Notification templates/messages (**should be persistent**)
- Future integrations (SMS, webhook, etc.)

**Backend Changes / Implementation Steps:**
- [x] Add `notifications` table to schema in `src/database.py` [implemented]
- [x] Write migration script to add `notifications` table [implemented]
- [x] Implement persistent notification settings logic in `src/alarms.py` and `src/database.py` [implemented]
- [x] Update notification API endpoints in `src/main.py` to support persistent settings [implemented]
- [x] Implement real email delivery in `AlarmManager.notify` using SMTP [implemented]
- [x] Add/extend tests for persistent notification settings and email delivery in `tests/test_alarms.py` [implemented]

---

## 5. Event-Triggered Frame Storage
**Implemented:**
- Pre-alarm and post-alarm frame capture (basic framework)
- Storage of event frames linked to alarm events (DB)

**Planned:**
- Efficient retrieval and download of event data
- API endpoints for event frame access
- Download/export selected frame(s) as PNG image(s) for a given time segment or event

**Backend Changes:**
- `src/frames.py`: Enhance EventTriggeredStorage class.
- `src/database.py`: Update thermal_frames schema as needed.
- `src/main.py`: API endpoints for event frame access and PNG export.

---

## 6. Historical Data & Analytics
**Implemented:**
- Analytics endpoints: `/api/v1/analytics/heatmap`, `/api/v1/analytics/trends`, `/api/v1/analytics/anomalies` (GET)
- Reports endpoint: `/api/v1/reports` (GET, supports summary, trend, anomaly_count)
- Frame export with overlay stats: `/api/v1/frames/export?overlay=stats` (GET, returns CSV with per-frame statistics)
- Query and view historical temperature data (by time, zone)
- Download/export historical data (CSV, JSON)
- Visual analytics (charts, heatmaps)

**Planned:**
- Download/export a time segment as PNG image(s)
- Event/alarm timeline view

**Backend Changes:**
- `src/database.py`: Efficient queries for historical/analytics data.
- `src/main.py`: API endpoints for analytics, reporting, and data export.
- `src/frames.py`: Analytics/statistics logic.

---

## 7. System Health Monitoring
**Implemented:**
- Health check API endpoint (sensor, database, buffer, alarms)
- Self-test and diagnostics routines (basic)

**Planned:**
- Error/warning log retrieval

**Backend Changes:**
- `src/monitor.py`: SystemMonitor class with health checks.
- `src/main.py`: `/api/v1/health` endpoint.

---

## 8. Settings Management
**Implemented:**
- Sensor mode (real/mock) via environment variable

**Planned:**
- User-configurable system settings (notification, database, buffer, alarm/event retention)
- Settings persistence and validation
- API endpoints for settings CRUD

**Backend Changes:**
- `src/database.py`: Store/retrieve settings.
- `src/main.py`: API endpoints for settings CRUD.

---

## 9. Database & Maintenance
**Implemented:**
- Database tuning (PRAGMA, vacuum)

**Planned:**
- SQLite database management (status, backup, restore, migration)
- Data retention and cleanup (automatic/manual)
- Storage location configuration
- Migration tools for schema updates

**Backend Changes:**
- `src/database.py`: PRAGMA optimization, backup/restore/migration.
- `src/main.py`: API endpoints for DB ops.

---

## 10. Testing & Quality Assurance
**Implemented:**
- Automated unit and integration tests for all modules (core features)
- API contract tests (basic)
- End-to-end system tests (mock sensor, simulated alarms)

**Planned:**
- Test coverage reporting
- Manual QA checklist
- Expanded coverage for new/advanced features

**Testing Coverage Goals:**
- Target: ≥90% code coverage for all backend modules
- All API endpoints must have request/response and error path tests
- Each module (alarms, zones, frames, database, monitor) should have dedicated unit and integration tests
- Add/extend tests for new features as they are implemented

**Backend Changes:**
- `tests/`: Extend/maintain tests for all modules and endpoints

## How to Use This Checklist
- Add new items as atomic, actionable steps.
- Mark items as `[x]` when done, `[~]` when in progress.
- Cross-reference code (API, DB, class/function) using `[see: ...]`.
- Group by feature for clarity.
- Update status and owner if collaborating.
- Add example payloads/specs inline or link to API table as needed.
- Update this note as process evolves.

## Real-Time Monitoring
- [x] Backend: Add FastAPI endpoint `/api/v1/thermal/real-time` in `src/main.py` [implemented]
- [x] Backend: Add FastAPI endpoint `/api/v1/zones/{zone_id}/average` in `src/main.py` [implemented]
- [x] Backend: Implement `get_latest_frame()` in `src/frames.py` [implemented]
- [x] Backend: Implement `get_zone_average()` in `src/zones.py` [implemented]
- [x] Add/extend tests: `test_real_time_frame` in `tests/test_api.py` [implemented]
- [x] Add/extend tests: `test_compute_zone_average` in `tests/test_zones.py` [implemented]

## Zone Management (Migrate in-memory to persistent)
- [x] Backend: Add FastAPI endpoints `/api/v1/zones` (GET/POST/DELETE) in `src/main.py` [implemented]
- [x] Backend: Implement `ZoneManager.add_zone`, `remove_zone`, `get_zones` in `src/zones.py` [implemented]
- [x] Backend: Update DB schema: add `enabled`, `threshold` to `zones` table in `src/database.py` [implemented]
- [x] Backend: Write migration script to add `enabled`, `threshold` columns to existing DB [implemented]
- [x] Backend: Refactor `ZoneManager` and `ZoneDatabase` in `src/zones.py` to read/write `enabled`, `threshold` from DB [implemented]
- [x] Backend: Update CRUD API endpoints in `src/main.py` to support persistent zone attributes [implemented]
- [x] Add/extend tests for persistent zone attributes in `tests/test_zones.py` [implemented]

## Alarm System (Migrate in-memory to persistent)
- [x] Backend: Update DB schema: add `cooldown_period`, `last_triggered`, `acknowledged`, `acknowledged_at` to `alarms` table in `src/database.py` [implemented]
- [x] Backend: Write migration script for alarm table changes [implemented]
- [x] Backend: Refactor `AlarmManager` and `AlarmEvent` in `src/alarms.py` to persist cooldown/acknowledge state [implemented]
- [x] Backend: Implement persistent alarm acknowledge/reset logic in API (`src/main.py`) [implemented]
- [x] Add/extend tests for persistent alarm state in `tests/test_alarms.py` [implemented]

## Notifications (Implement persistent settings)
- [x] Backend: Add `notifications` table to schema in `src/database.py` [implemented]
- [x] Backend: Write migration script to add `notifications` table [implemented]
- [x] Backend: Implement persistent notification settings logic in `src/alarms.py` and `src/database.py` [implemented]
- [x] Update notification API endpoints in `src/main.py` to support persistent settings [implemented]
- [x] Implement real email delivery in `AlarmManager.notify` using SMTP [implemented]
- [x] Add/extend tests for persistent notification settings and email delivery in `tests/test_alarms.py` [implemented]

## Event-Triggered Frame Storage
- [x] Backend: Add FastAPI endpoints `/api/v1/events/{event_id}/frames`, `/api/v1/events/{event_id}/frames.png` in `src/main.py` [implemented]
- [x] Backend: Basic `EventTriggeredStorage` framework in `src/frames.py` [implemented - basic only]
- [x] Backend: Update DB schema: add `thermal_frames` table [implemented - basic only]
- [x] Add/extend tests: `test_event_triggered_storage` in `tests/test_frames.py` [implemented]

## Historical Data & Analytics
- [x] Backend: Add FastAPI endpoint `/api/v1/frames/export` in `src/main.py` [implemented: CSV export]
    - [x] Define Pydantic request/response models [see: API table]
    - [x] Add route and handler in `main.py` [see: main.py]
    - [x] Implement efficient DB query in `database.py` [see: database.py]
    - [x] Add/extend tests: `test_historical_export` in `tests/test_api.py`  # PNG/overlay export planned

## System Health Monitoring
- [x] Backend: Add FastAPI endpoint `/api/v1/health` in `src/main.py` [implemented]
- [x] Backend: Implement `HealthChecker.check_health`, `get_status` in `src/monitor.py` [implemented]

## Settings Management
- [x] Backend: Add FastAPI endpoints `/api/v1/settings` (GET/POST) in `src/main.py` [implemented]
    - [x] Define Pydantic models for settings [see: API table]
    - [x] Add route and handler in `main.py`
    - [x] Implement CRUD logic in `database.py`
    - [x] Add/extend tests: `test_settings_crud` in `tests/test_api.py`

## Database & Maintenance
- [x] Backend: Add FastAPI endpoints `/api/v1/database/backup`, `/api/v1/database/restore`, `/api/v1/database/migrate` in `src/main.py` [implemented]
    - [x] Define request/response models [see: API table]
    - [x] Add routes and handlers in `main.py`
    - [x] Implement backup/restore/migration logic in `database.py`
    - [ ] Add/extend tests: `test_database_backup_restore` in `tests/test_database.py`

## Testing & Quality Assurance
- [~] Backend: Add/extend unit/integration tests for all modules in `tests/` [in progress]
- [ ] Backend: Add API contract and E2E tests (mock sensor, simulated alarms) in `tests/` [planned]
- [ ] Backend: Add/extend test coverage reporting [planned]
- [ ] Manual QA checklist [planned]

## Advanced Analytics & Reporting (Planned)
- [x] Backend: Add Pydantic models for analytics/reporting requests and responses in `src/main.py` [implemented]
- [x] Backend: Add FastAPI endpoints in `src/main.py` for:
    - [x] `/api/v1/analytics/heatmap` (GET) [implemented]
    - [x] `/api/v1/analytics/trends` (GET) [implemented]
    - [x] `/api/v1/analytics/anomalies` (GET) [implemented]
    - [x] `/api/v1/reports` (GET) [implemented]
    - [x] `/api/v1/frames/export?overlay=stats` (GET) [implemented]
- [x] Backend: Implement heatmap/trend/anomaly logic in `src/frames.py` [implemented]
- [x] Backend: Implement report generation in `src/database.py` [implemented]
- [x] Backend: Add overlay logic for CSV export in `src/frames.py` [implemented]
- [x] Backend: Add/extend DB schema for analytics/reporting as needed in `src/database.py` [implemented]
- [x] Backend: Add/extend tests: `test_analytics_endpoints` in `tests/test_frames.py`, `tests/test_api.py` [implemented]

---

# Document Changelog
| Date       | Author      | Summary of Changes                                                      |
|------------|-------------|------------------------------------------------------------------------|
| 2025-06-12 | Copilot     | Removed all frontend/UI references, improved backend focus and clarity  |
| 2025-06-11 | Copilot     | Major refactor: granular checklists, endpoint specs, changelogs, status |
| 2025-06-11 | Copilot     | Refined frontend mapping, made checklists atomic, added open questions, glossary, and improved changelog granularity |
| 2025-06-11 | GitHub Copilot | **ACCURACY CORRECTIONS**: Fixed status claims to match actual implementation, corrected database schema documentation, updated frontend technology references from Vue.js to React, added implementation status disclaimers |
| 2025-06-12 | Copilot     | Implemented /api/v1/frames/export (CSV), updated checklist and API table           |

---

# Database Schema Changelog

## Current Schema (As Implemented)

### Zones Table (current implementation - basic)
```sql
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#FF0000'
    -- Note: enabled, threshold fields are handled in-memory by ZonesManager
);
```

### Alarms Table (current implementation - basic)
```sql
CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id INTEGER,
    enabled INTEGER DEFAULT 1,
    threshold REAL,
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);
```

### Thermal Frames Table (current implementation)
```sql
CREATE TABLE IF NOT EXISTS thermal_frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    frame BLOB,
    frame_size INTEGER,
    FOREIGN KEY (event_id) REFERENCES alarm_events(id)
);
```

## 2025-06-11: Planned Schema Enhancements

### Enhanced Alarms Table (planned for v1.2)
```sql
-- Planned upgrade to alarms table with advanced features
CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    zone_id INTEGER,
    alarm_type TEXT,           -- 'threshold', 'zone_compare', 'system'
    threshold_min REAL,
    threshold_max REAL,
    enabled BOOLEAN DEFAULT 1,
    pre_alarm_duration INTEGER DEFAULT 300  -- Seconds before alarm to store
    post_alarm_duration INTEGER DEFAULT 300 -- Seconds after alarm to store
    cooldown_period INTEGER DEFAULT 600,     -- Minimum seconds between triggers (debounce)
    last_triggered DATETIME,                 -- Last time this alarm was triggered
    trigger_count INTEGER DEFAULT 0,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at DATETIME,
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);
```

### Analytics Results Table (planned for advanced analytics)
```sql
CREATE TABLE IF NOT EXISTS analytics_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- e.g., 'heatmap', 'trend', 'anomaly', 'report'
    params TEXT,                  -- JSON-encoded parameters for the analysis
    result_data BLOB,             -- Binary or JSON-encoded result
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Notifications Table (planned)
```sql
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,           -- 'email', 'webhook', 'sms'
    config TEXT,                  -- JSON-encoded configuration
    enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Changelog
- 2025-06-11: Documented current basic schema vs planned enhancements
- 2025-06-11: Clarified that some features (zone enabled/threshold) are currently in-memory only
- 2025-06-12: Note that `/api/v1/frames/export` (CSV) is implemented and uses the current `thermal_frames` schema

---

# Technical Appendix

## API Endpoint Table (Grouped by Feature)

## Real-Time Monitoring
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/thermal/real-time                | GET    | main.py          | Get latest thermal frame       | implemented |
| /api/v1/zones/{zone_id}/average          | GET    | main.py/zones.py | Get average temp for a zone    | implemented |

## Zone Management
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/zones                            | GET    | main.py/zones.py | List all zones                 | implemented |
| /api/v1/zones                            | POST   | main.py/zones.py | Create/update a zone           | implemented |
| /api/v1/zones/{zone_id}                  | DELETE | main.py/zones.py | Delete a zone                  | implemented |

## Alarm System
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/alarms/history                   | GET    | main.py/alarms.py| Get alarm history              | implemented |
| /api/v1/alarms/acknowledge               | POST   | main.py/alarms.py| Acknowledge/reset alarm        | implemented |

## Event-Triggered Frame Storage
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/events/{event_id}/frames         | GET    | main.py/frames.py| Get frames for an event        | implemented |
| /api/v1/events/{event_id}/frames.png     | GET    | main.py/frames.py| Download event frames as PNG   | implemented |
| /api/v1/events/{event_id}/frames/blobs   | GET    | main.py/frames.py| Get all frame blobs for event  | implemented |

## Historical Data & Analytics
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/frames/export                    | GET    | main.py/frames.py| Export frames as CSV           | implemented |
| /api/v1/frames/export?overlay=stats      | GET    | main.py/frames.py| Export frames with per-frame stats (CSV) | implemented |
| /api/v1/analytics/heatmap                | GET    | main.py/frames.py| Generate/export heatmap        | implemented |
| /api/v1/analytics/trends                 | GET    | main.py/frames.py| Get temperature trends         | implemented |
| /api/v1/analytics/anomalies              | GET    | main.py/frames.py| Detect/report anomalies        | implemented |
| /api/v1/reports                          | GET    | main.py/database.py| Generate report               | implemented |

## Notifications
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/notifications/settings           | GET/POST| main.py/alarms.py| Get/set notification config    | implemented |

## System Health Monitoring
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/health                           | GET    | main.py/monitor.py| System health check           | implemented |

## Settings Management
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/settings                         | GET/POST| main.py/database.py| Get/set system settings       | implemented |

## Database & Maintenance
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/database/backup                  | POST   | main.py/database.py| Trigger DB backup             | implemented |
| /api/v1/database/restore                 | POST   | main.py/database.py| Restore DB from backup        | implemented |
| /api/v1/database/migrate                 | POST   | main.py/database.py| Run DB migration              | implemented |

---

## Frame Format
- Each frame is a 32x24 array of float32 values (row-major order).
- Binary storage: frames are stored as raw float32[768] in the database (BLOB).
- API transport: frames are base64-encoded for JSON transport (e.g., in `/frames/blobs`).
- PNG export: frames are normalized to 8-bit grayscale for image export.
- Metadata: each frame includes `id`, `event_id`, `timestamp`, `frame_size`, and the encoded frame data.
- Timestamps and order are preserved for correct playback and analytics.

---

# Backend Feature Status (2025-06-12)
- All zone, alarm, notification (including real email delivery), and event frame features are now persistent (SQLite)
- All API endpoints use dependency injection for database access (FastAPI Depends)
- Automated tests cover all persistent features and run in full isolation
- No in-memory storage is used for zones, alarms, notifications, or event frames
- Event frame APIs and PNG export are fully tested
- Email notifications are sent on alarm events using SMTP (Gmail App Passwords supported)

---

## Notifications
| Endpoint                                 | Method | Handler Location | Purpose                        | Status      |
|------------------------------------------|--------|------------------|--------------------------------|-------------|
| /api/v1/notifications/settings           | GET/POST| main.py/alarms.py| Get/set notification config    | implemented |

---

**Email Notification Delivery:**
- Configure SMTP settings via environment variables or notification config (supports Gmail App Passwords).
- When an alarm triggers, the backend sends a real email to the configured recipient(s).
- Delivery errors are logged; see logs for troubleshooting.
