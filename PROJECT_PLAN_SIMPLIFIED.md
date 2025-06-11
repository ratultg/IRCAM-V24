# IR Thermal Monitoring System - Simplified Project Plan

> **Project:** 24/7 IR Thermal Monitoring Application  
> **Hardware:** Raspberry Pi 5 + MLX90640 Thermal Camera  
> **Timeline:** 16 weeks (realistic scope)  
> **Status:** Planning Phase

---

## 🎯 Project Overview

Build a reliable 24/7 thermal monitoring system that provides real-time thermal visualization, zone-based temperature tracking, historical data analysis, and intelligent alerting.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│            Web Interface (FastAPI)         │
│   Real-time View | History | Settings      │
└─────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────┐
│           Application Layer                 │
│   Sensor | Zone Engine | Alarms | Data     │
└─────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────┐
│             Data Layer                      │
│   SQLite Database | Config | Logs          │
└─────────────────────────────────────────────┘
```

## 🔧 Core Features

### 1. **Real-time Thermal Visualization**
- Live thermal camera display (32x24 resolution)
- Multiple color palettes (Jet, Iron, Rainbow)
- 1-8 FPS configurable refresh rate
- Temperature cursor tracking

### 2. **Zone Management**
- Allow only 1-2 zones (no UI drawing for MVP)
- Draw Rectacgular zones on thermal view
- Real-time temperature calculation per zone
- Zone persistence and management

### 3. **Historical Data**
- Time-series temperature storage
- Interactive charts with date ranges
- Data export (CSV, JSON)
- Automated data cleanup and aggregation

### 4. **Thermal Frame Storage & Replay**
- Store full thermal frame data (768 temperature points)
- Historical image replay with timeline scrubber
- Configurable storage retention (1-30 days)
- Frame compression for storage efficiency
- Export thermal frames as images or data

### 5. **Alarm System**
- Threshold-based alarms (high/low temperature)
- Zone comparison alarms
- Email and webhook notifications
- Alarm logging and management

### 6. **System Monitoring**
- Sensor health monitoring
- Performance metrics
- Error tracking and recovery
- Remote access via Tailscale

## 📁 Project Structure

```
ir-monitoring-app/
├── backend/
│   ├── src/
│   │   ├── main.py                     # FastAPI application
│   │   ├── sensor.py                   # MLX90640 handler + mock sensor
│   │   ├── database.py                 # All DB operations (single file)  
│   │   ├── zones.py                    # Zone management (single file)
│   │   ├── alarms.py                   # Alarm logic (single file)
│   │   ├── frames.py                   # Thermal frame storage & replay
│   │   ├── monitor.py                  # System monitoring & health checks
│   │   └── static/                     # CSS/JS assets
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Main React app
│   │   ├── components/                 # React components (ThermalView, ZoneList, etc.)
│   │   ├── api/                        # API calls (axios/fetch)
│   │   └── ...
│   ├── public/
│   └── package.json
├── scripts/
│   ├── install.sh                      # Production Pi setup
│   ├── backup.sh                   # Database backup automation
│   ├── dev-setup.py                # Local development environment
│   └── systemd/                    # Service configuration files
├── tests/
│   ├── test_sensor.py              # Sensor and mock testing
│   ├── test_database.py            # Database operations testing
│   └── test_integration.py         # End-to-end testing
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── .env.template                   # Configuration template
└── README.md                       # Setup and operation guide
```

## 💾 Database Design

### **Enhanced Schema (4 Core Tables)**
- **thermal_data**: Temperature readings (zone averages, time-series)
- **thermal_frames**: Full frame data for replay (768 temp points)
- **zones**: Zone definitions (max 2 zones for MVP)
- **alarms**: Alarm configs and events combined

### **Complete Database Schema**
```sql
-- Zone temperature data (aggregated, lightweight)
CREATE TABLE thermal_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    zone_id INTEGER,
    min_temp REAL,
    max_temp REAL,
    avg_temp REAL,
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);

-- Event-triggered thermal frame storage for replay
CREATE TABLE thermal_frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    frame_data BLOB,           -- Compressed 768 temperature values
    min_temp REAL,             -- Frame statistics for quick filtering
    max_temp REAL,
    avg_temp REAL,
    frame_size INTEGER,        -- Compressed data size in bytes
    event_id INTEGER,          -- Link to triggering alarm event
    event_phase TEXT,          -- 'pre-alarm', 'post-alarm', or 'continuous'
    FOREIGN KEY (event_id) REFERENCES alarm_events(id)
);

-- Alarm event records (separate from alarm configurations)
CREATE TABLE alarm_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alarm_id INTEGER,          -- Which alarm configuration triggered
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    severity TEXT,             -- 'low', 'medium', 'high', 'critical'
    trigger_value REAL,        -- Temperature that triggered alarm
    zone_id INTEGER,
    description TEXT,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at DATETIME,
    pre_frames_stored INTEGER DEFAULT 0,  -- Count of pre-alarm frames
    post_frames_stored INTEGER DEFAULT 0, -- Count of post-alarm frames
    FOREIGN KEY (alarm_id) REFERENCES alarms(id),
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);
    frame_size INTEGER         -- Compressed data size in bytes
);

-- Zone definitions
CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    x1 INTEGER, y1 INTEGER,    -- Top-left corner
    x2 INTEGER, y2 INTEGER,    -- Bottom-right corner
    color TEXT DEFAULT '#FF0000',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT 1
    -- For MVP: Enforce max 2 zones in application logic
);

-- Alarm configurations  
CREATE TABLE alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    zone_id INTEGER,
    alarm_type TEXT,           -- 'threshold', 'zone_compare', 'system'
    threshold_min REAL,
    threshold_max REAL,
    enabled BOOLEAN DEFAULT 1,
    pre_alarm_duration INTEGER DEFAULT 300,  -- Seconds before alarm to store
    post_alarm_duration INTEGER DEFAULT 300, -- Seconds after alarm to store
    cooldown_period INTEGER DEFAULT 600,     -- Minimum seconds between triggers
    last_triggered DATETIME,
    trigger_count INTEGER DEFAULT 0,
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);

-- Essential indexes for performance
CREATE INDEX idx_thermal_data_timestamp ON thermal_data(timestamp);
CREATE INDEX idx_thermal_data_zone_time ON thermal_data(zone_id, timestamp);
CREATE INDEX idx_thermal_frames_timestamp ON thermal_frames(timestamp);
CREATE INDEX idx_thermal_frames_event ON thermal_frames(event_id);
CREATE INDEX idx_thermal_frames_phase ON thermal_frames(event_phase);
CREATE INDEX idx_alarm_events_timestamp ON alarm_events(timestamp);
CREATE INDEX idx_alarm_events_alarm_id ON alarm_events(alarm_id);
CREATE INDEX idx_zones_active ON zones(active);
CREATE INDEX idx_alarms_enabled ON alarms(enabled);

-- SQLite optimization settings
PRAGMA journal_mode = WAL;        -- Better concurrent access
PRAGMA synchronous = NORMAL;      -- Balance safety vs performance
PRAGMA cache_size = 10000;        -- 10MB memory cache
PRAGMA temp_store = memory;       -- Use RAM for temp operations
```

### **Event-Triggered Frame Storage** 🎯
**Philosophy**: Store thermal frames only around alarm events (5 minutes before + 5 minutes after) instead of continuous storage for 97% storage reduction while preserving all critical thermal data.

#### **Storage Architecture**
- **Circular Buffer**: Keep last 5 minutes of frames in RAM
- **Event Trigger**: When alarm occurs, persist buffer + continue recording for 5 more minutes
- **Memory Management**: Rolling window buffer (5-10MB RAM usage)
- **Configurable Windows**: Pre-alarm and post-alarm durations (default: 5min each)

#### **Storage Calculations**
```python
# MLX90640 Frame Size
THERMAL_POINTS = 32 * 24 = 768
COMPRESSED_FRAME_SIZE = ~920 bytes (70% compression)

# Event-Triggered Storage (10 minutes per alarm event)
PRE_ALARM_DURATION = 5 minutes = 300 seconds
POST_ALARM_DURATION = 5 minutes = 300 seconds
TOTAL_EVENT_DURATION = 600 seconds

# Storage per alarm event
2 FPS: 2 * 600 * 920 bytes = ~1.1MB per event
4 FPS: 4 * 600 * 920 bytes = ~2.2MB per event

# Daily storage (assuming typical alarm frequency)
1 alarm/day:  1.1-2.2MB/day   (99% reduction vs continuous)
3 alarms/day: 3.3-6.6MB/day   (98% reduction vs continuous)
5 alarms/day: 5.5-11MB/day    (97% reduction vs continuous)
```

#### **Storage Comparison: Continuous vs Event-Triggered**
| Frame Rate | Continuous Storage | Event-Triggered (5 alarms/day) | Reduction |
|------------|-------------------|--------------------------------|-----------|
| 2 FPS | 160MB/day, 4.8GB/month | 5.5MB/day, 165MB/month | **97%** |
| 4 FPS | 320MB/day, 9.6GB/month | 11MB/day, 330MB/month | **97%** |

#### **Benefits of Event-Triggered Storage**
- **Massive storage savings**: 97-99% reduction in storage requirements
- **Focus on important data**: Only store frames around actual incidents  
- **Extended retention**: Store 6-12 months of event data in same space
- **Better performance**: Minimal disk I/O, faster database operations
- **Complete context**: 5 minutes before shows what led to alarm
- **Scalable**: Works with any alarm frequency without storage explosion

#### **Implementation Architecture**
```python
# Event-Triggered Frame Storage System
class ThermalFrameBuffer:
    """Circular buffer for pre-alarm frame storage in memory"""
    def __init__(self, duration_seconds=300, fps=2):
        self.max_frames = duration_seconds * fps
        self.buffer = deque(maxlen=self.max_frames)
        
    def add_frame(self, frame_data, timestamp):
        """Add frame to circular buffer"""
        self.buffer.append((timestamp, frame_data))
        
    def dump_to_storage(self, event_id):
        """Store all buffered frames as pre-alarm data"""
        for timestamp, frame_data in self.buffer:
            store_frame(frame_data, timestamp, event_id, 'pre-alarm')

class EventTriggeredStorage:
    """Main storage coordinator for alarm events"""
    def __init__(self):
        self.frame_buffer = ThermalFrameBuffer()
        self.active_events = {}  # Track ongoing post-alarm recording
        
    def on_thermal_frame(self, frame_data, timestamp):
        """Handle each thermal frame"""
        # Always add to circular buffer
        self.frame_buffer.add_frame(frame_data, timestamp)
        
        # Store post-alarm frames for active events
        for event_id in self.active_events:
            store_frame(frame_data, timestamp, event_id, 'post-alarm')
            
    def on_alarm_triggered(self, alarm_event):
        """Handle alarm event - start event-triggered storage"""
        event_id = alarm_event.id
        
        # 1. Dump pre-alarm buffer to storage
        self.frame_buffer.dump_to_storage(event_id)
        
        # 2. Start post-alarm recording
        post_duration = alarm_event.alarm.post_alarm_duration
        end_time = time.time() + post_duration
        self.active_events[event_id] = end_time
        
    def cleanup_expired_events(self):
        """Remove completed post-alarm recordings"""
        current_time = time.time()
        self.active_events = {
            eid: end_time for eid, end_time in self.active_events.items()
            if end_time > current_time
        }
```

### **Performance Optimizations**
- **Memory-efficient circular buffer**: Fixed-size deque for pre-alarm frames
- **Batch database operations**: Store frames in batches during high-activity periods
- **Asynchronous storage**: Non-blocking frame persistence using background tasks
- **Configurable compression**: GZIP compression for frame data (70% size reduction)
- **Event overlap handling**: Smart merging of overlapping alarm events
- **Background cleanup**: Automatic removal of old event data based on retention policy

## 🚀 Development Timeline (16 Weeks Total)

### **Phase 0: Development Environment (Weeks 1-2)**
- [ ] **Local development setup** with mock sensor
- [ ] **Project structure** and basic FastAPI skeleton
- [ ] **Database schema** implementation and testing
- [ ] **Development workflow** (hot-reload, testing, debugging)
- [ ] **Mock thermal data** generation for testing

### **Phase 1: Core Foundation (Weeks 3-5)**
- [ ] **Real MLX90640 sensor** integration on Pi
- [ ] **Basic thermal visualization** with HTML5 Canvas
- [ ] **Database operations** (CRUD for all tables)
- [ ] **Simple web dashboard** with live thermal display
- [ ] **Basic error handling** and logging

### **Phase 2: Essential Features (Weeks 6-9)**
- [ ] **Zone drawing** functionality on thermal display
- [ ] **Real-time temperature** calculation per zone
- [ ] **Basic alarm system** with threshold monitoring
- [ ] **Historical data storage** and simple charts
- [ ] **Configuration management** via environment variables

### **Phase 3: Event-Triggered Frame Storage (Weeks 10-12)**
- [ ] **Circular buffer implementation** for pre-alarm frame storage
- [ ] **Event-triggered storage system** with alarm integration
- [ ] **Frame replay interface** with event-based navigation
- [ ] **Storage management** (cleanup, retention policies)
- [ ] **Performance optimization** for minimal disk I/O

### **Phase 4: Production Ready (Weeks 13-15)**
- [ ] **Email alarm system** integration (using existing alarms.py)
- [ ] **Event management interface** (acknowledge, analyze, annotate events)
- [ ] **Advanced replay features** (event timeline, frame comparison)
- [ ] **Data export** functionality (event reports, thermal images)
- [ ] **System health monitoring** and alerts
- [ ] **Deployment automation** (systemd service, scripts)
- [ ] **Backup and recovery** procedures
- [ ] **Documentation** and troubleshooting guides

### **Phase 5: Testing & Launch (Week 16)**
- [ ] **End-to-end testing** on production Pi
- [ ] **Performance validation** and optimization
- [ ] **Final bug fixes** and stability improvements
- [ ] **Production deployment** and monitoring setup

## 🛠️ Technology Stack

### **Backend**
- **Python 3.11+** (Native, no Docker)
- **FastAPI** (Modern async web framework, REST API)
- **SQLite** (Database)
- **WebSockets** (Real-time communication for live data)

### **Frontend**
- **React** (Component-based UI framework)
- **MUI (Material-UI)** (Material Design component library for React)
- **react-chartjs-2** (Charts for historical data)
- **Custom React components** for thermal visualization (using HTML5 Canvas or SVG)

### **Hardware**
- **Raspberry Pi 5** (Host system)
- **MLX90640** (Thermal sensor)
- **I2C Interface** (Sensor communication)

### **Deployment**
- **Systemd** (Service management for backend)
- **Tailscale** (Secure remote access)
- **Serve React static build** via FastAPI or a simple static file server

---

### **Frontend/Backend Architecture**
- The **React** frontend communicates with the **FastAPI** backend via REST API endpoints (for data, configuration, etc.) and WebSockets (for real-time thermal frames and alarms).
- The frontend is a separate project (e.g., `/frontend`), built and deployed as static files.
- The backend serves the API and, optionally, the static frontend build.

---

### **Frontend Features (React + MUI)**
- **Material Design dashboard**: Modern, responsive UI using MUI components.
- **Thermal View**: Custom React component using Canvas or SVG for live thermal visualization.
- **Zone Management**: Simple zone list and configuration (no drag-and-drop for MVP).
- **Historical Charts**: Use `react-chartjs-2` for time-series and event data.
- **Alarm Log**: Material Table for alarm/event history.
- **Settings**: Material UI forms for configuration.

---

### **Project Structure (Updated)**
```
ir-monitoring-app/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI app (API + WebSocket)
│   │   ├── ...               # Sensor, DB, alarms, etc.
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React app
│   │   ├── components/       # React components (ThermalView, ZoneList, etc.)
│   │   ├── api/              # API calls (axios/fetch)
│   │   └── ...
│   ├── public/
│   └── package.json
├── scripts/
│   ├── install.sh
│   └── ...
└── ...
```

---

### **Development Workflow (Updated)**
- **Backend**: Run FastAPI server (with hot reload for development).
- **Frontend**: Run React dev server (`npm start` or `yarn start` in `/frontend`).
- **Production**: Build React app (`npm run build`), serve static files via FastAPI or a static server.

---

### **Notes**
- **HTMX** and **Bootstrap** are removed in favor of React + MUI.
- All UI/UX is handled in React; backend only provides API/data.
- For MVP, keep zone management simple (config or basic form, no drag-and-drop).
- Use MUI DataGrid, Dialogs, and Cards for a modern dashboard look.

## 🚧 Known Challenges & Mitigation Strategies

### **Technical Challenges**
1. **I2C Reliability**: Bus errors and sensor communication failures
   - *Mitigation*: Automatic bus reset, retry logic, watchdog monitoring
   
2. **Memory Management**: Python memory leaks during 24/7 operation  
   - *Mitigation*: Regular service restart (daily), memory monitoring, garbage collection
   
3. **SD Card Wear**: Frequent database writes causing card failure
   - *Mitigation*: WAL mode, write optimization, high-quality cards, wear monitoring
   
4. **Thermal Management**: Pi 5 heat affecting sensor readings
   - *Mitigation*: Proper case ventilation, thermal monitoring, sensor positioning

### **Operational Challenges**
5. **Network Connectivity**: Loss of remote access during failures
   - *Mitigation*: Local monitoring, Tailscale redundancy, local recovery procedures
   
6. **Storage Management**: Unexpected storage growth or cleanup failures
   - *Mitigation*: Storage monitoring, manual cleanup procedures, alert thresholds
   
7. **User Error**: Misconfiguration or accidental system changes
   - *Mitigation*: Configuration backups, automated setup scripts, documentation

### **Risk Assessment Matrix**
| Risk | Probability | Impact | Mitigation Priority |
|------|-------------|--------|-------------------|
| I2C sensor failure | Medium | High | 🔴 Critical |
| SD card corruption | Medium | High | 🔴 Critical |
| Memory leaks | High | Medium | 🟡 Important |
| Storage overflow | Low | Medium | 🟡 Important |
| Network issues | Low | Low | 🟢 Monitor |

## 📚 Resources & Documentation

### **Hardware Documentation**
- [MLX90640 Sensor Documentation](https://github.com/pimoroni/mlx90640-library)
- [Raspberry Pi 5 Setup Guide](https://www.raspberrypi.org/documentation/)
- [I2C Interface Configuration](https://www.raspberrypi.org/documentation/configuration/raspi-config.md)

### **Software Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Performance Tuning](https://www.sqlite.org/pragma.html)
- [Systemd Service Management](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

### **Project Documentation** (To Be Created)
- **README.md**: Quick start and basic usage
- **INSTALL.md**: Detailed installation procedures
- **OPERATIONS.md**: Day-to-day operation and maintenance
- **TROUBLESHOOTING.md**: Common issues and solutions
- **API.md**: FastAPI endpoint documentation
- **ARCHITECTURE.md**: Technical system design details

---

> **Note:** This plan provides a realistic 16-week timeline with proper development environment setup, accurate storage calculations, comprehensive operational procedures, and detailed deployment strategies. The focus is on building a robust, maintainable system that actually works in production rather than an overly ambitious plan that fails in practice.
