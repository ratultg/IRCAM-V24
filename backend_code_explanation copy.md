# IR Thermal Monitoring System Backend: Subsystem Logic Overviews (Non-Programmer Friendly)

This document explains how each part of the backend system works, step by step, in plain language. It is designed for anyone who wants to understand the system, even without a programming background.

---

## 1. Sensor Handling

### What is it?
This part of the system is responsible for reading temperature data from a special camera (the MLX90640 sensor) or, for testing, generating fake temperature data.

### How does it work?
1. **Choosing the Data Source**
   - When the system starts, it checks if it should use the real sensor or a fake one (for testing). This is controlled by a setting called `MOCK_SENSOR`.
2. **Getting a Temperature Snapshot**
   - The system asks the sensor for a snapshot, which is a grid of 768 temperature values (imagine a thermal photo).
3. **Handling Problems**
   - If the sensor fails or has trouble, the system tries again and records any errors for later review.

### In Simple Terms
- The system can use a real camera or a fake one for testing.
- It takes a thermal snapshot on request.
- If something goes wrong, it tries again and keeps a record of the problem.

---

## 2. Frame Buffering

### What is it?
This is like a rolling photo album that always keeps the most recent thermal snapshots.

### How does it work?
1. **Setting Up the Album**
   - The system creates a special memory area that can hold about 10 minutes of snapshots.
2. **Saving New Snapshots**
   - Every time a new snapshot is taken, it is added to the album. If the album is full, the oldest snapshot is thrown out to make room for the new one.
3. **Looking Back in Time**
   - The system can quickly look back at the most recent snapshots, which is useful if something important happens.

### In Simple Terms
- The system always keeps the latest 10 minutes of thermal images.
- New images replace the oldest ones.
- It can quickly find recent images if needed.

---

## 3. Zone Management

### What is it?
Zones are special areas on the thermal image that you want to watch closely (for example, a machine or doorway).

### How does it work?
1. **Defining Zones**
   - Users can draw up to two rectangles on the thermal image to mark areas of interest.
2. **Saving Zones**
   - These zones are saved so the system remembers them, even if restarted.
3. **Watching Zones**
   - For every new snapshot, the system checks the temperature inside each zone.

### In Simple Terms
- You can tell the system which areas to watch.
- The system remembers these areas.
- It checks the temperature in each area every time it takes a new snapshot.

---

## 4. Alarm System

### What is it?
This part watches for temperatures that are too high in your zones and alerts you if something is wrong.

### How does it work?
1. **Setting Temperature Limits**
   - You can set a maximum temperature for each zone.
2. **Checking Temperatures**
   - Every time a new snapshot is taken, the system checks if any zone is too hot.
3. **Triggering an Alarm**
   - If a zone is too hot, the system records an alarm event with details (when, where, how hot).
4. **Sending Alerts**
   - The system is ready to send alerts (like emails), but this is currently just a placeholder.
5. **Starting Event Recording**
   - When an alarm happens, the system prepares to save extra data before and after the event.

### In Simple Terms
- You set temperature limits for important areas.
- The system checks these limits every time.
- If a limit is crossed, it records an alarm and prepares to save more data.

---

## 5. Event-Triggered Frame Storage

### What is it?
This part saves a "movie" of what happened before and after an alarm.

### How does it work?
1. **Saving Before the Alarm**
   - When an alarm happens, the system grabs the last 5 minutes of snapshots from its album.
2. **Saving After the Alarm**
   - It then keeps saving new snapshots for the next 5 minutes.
3. **Storing the Event**
   - Both sets of snapshots (before and after) are saved together in the database, linked to the alarm.
4. **Not Slowing Down**
   - The system does this in the background so it doesn’t slow down other work.

### In Simple Terms
- When something important happens, the system saves what it saw before and after.
- This lets you review the whole event later, like watching a replay.

---

## 6. Database & Persistence

### What is it?
This is the system’s memory, where it saves all important information so nothing is lost.

### How does it work?
1. **Setting Up the Database**
   - The system uses a reliable database (SQLite) and tunes it for speed and safety.
2. **Organizing Information**
   - It creates tables for snapshots, events, alarms, and zones.
3. **Safe Saving**
   - Every time it saves or updates information, it does so in a way that protects against data loss.

### In Simple Terms
- All important data is saved in a safe, organized way.
- The system is designed to avoid losing data, even if something goes wrong.

---

## 7. API Layer

### What is it?
This is how other programs (like a web dashboard) talk to the backend to get data or control it.

### How does it work?
1. **Providing Access**
   - The system offers a set of web addresses (endpoints) where you can ask for data or send commands.
2. **Choosing the Sensor**
   - The system automatically uses the real or fake sensor, depending on the settings.
3. **Checking Inputs**
   - It checks all requests to make sure they are valid and safe.

### In Simple Terms
- The backend can be controlled and monitored from other programs or dashboards.
- It always checks that requests are safe and make sense.

---

## 8. System Health Monitoring

### What is it?
This part checks that all other parts of the system are working correctly.

### How does it work?
1. **Regular Checks**
   - The system regularly checks the sensor, database, frame buffer, and alarm system.
2. **Making a Report**
   - It combines the results into a single health report.
3. **Sharing the Report**
   - The health report is available through the API for anyone who needs to monitor the system.

### In Simple Terms
- The system keeps an eye on itself and reports if anything is wrong.

---

## 9. Testing & Quality Assurance

### What is it?
This ensures the system works correctly and is reliable.

### How does it work?
1. **Testing Each Part**
   - Every part of the system is tested separately to make sure it works.
2. **Testing Everything Together**
   - The whole system is tested as a unit to make sure all parts work together.
3. **Keeping Quality High**
   - The system is checked for mistakes, and the code is kept clean and organized.

### In Simple Terms
- The system is thoroughly tested to make sure it works and is reliable.

---

## Appendix: Classes, Methods, and Functions Explained

Below is a table for each subsystem listing the main classes, methods, and functions, along with a plain-language explanation of what each does.

### 1. Sensor Handling
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| ThermalSensor          | Class    | Talks to the real MLX90640 sensor to get temperature data.                   |
| __init__               | Method   | Sets up the sensor and prepares it for use.                                  |
| read_frame             | Method   | Gets a new thermal snapshot (768 values) from the sensor.                    |
| MockThermalSensor      | Class    | Pretends to be a sensor, generating fake/random temperature data for testing. |
| __init__ (Mock)        | Method   | Sets up the mock sensor with default temperature and noise.                  |
| read_frame (Mock)      | Method   | Returns a fake thermal snapshot (random values).                             |

### 2. Frame Buffering
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| ThermalFrameBuffer     | Class    | Stores the most recent thermal snapshots in a rolling memory buffer.          |
| add_frame              | Method   | Adds a new snapshot to the buffer.                                           |
| get_last_n_frames      | Method   | Retrieves the most recent N snapshots.                                       |

### 3. Zone Management
| Method/Class            | Type     | Description                                                                 |
|-------------------------|----------|-----------------------------------------------------------------------------|
| add_zone                | Method   | Adds a new zone (rectangle) to watch. Now supports naming and color-coding each zone (fields: name, color). |
| remove_zone             | Method   | Removes a zone from the list.                                               |
| get_zones               | Method   | Returns all currently defined zones, including their names and colors (fields: name, color). |
| compute_zone_average    | Method   | Calculates the average temperature in a zone for a given snapshot.          |
| Zone                    | Class    | Represents a single rectangular area on the image, with a name and color.   |


### 4. Alarm System
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| AlarmManager           | Class    | Watches zones for high temperatures and triggers alarms.                     |
| check_thresholds       | Method   | Checks if any zone is too hot and should trigger an alarm.                   |
| log_event              | Method   | Records an alarm event in the system.                                        |
| notify                 | Method   | Sends an alert (currently a placeholder for future use).                     |
| AlarmEvent             | Class    | Represents a single alarm event (when, where, how hot, etc.).                |

### 5. Event-Triggered Frame Storage
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| EventTriggeredStorage  | Class    | Handles saving snapshots before and after an alarm event.                    |
| trigger_event          | Method   | Starts the process of saving pre- and post-alarm snapshots.                  |

### 6. Database & Persistence
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| Database               | Class    | Manages saving and loading all data (snapshots, events, alarms, zones).      |
| connect                | Method   | Opens a connection to the database.                                          |
| initialize_schema      | Method   | Sets up the tables and structure in the database.                            |
| execute_query          | Method   | Runs a command to save or get data.                                          |
| close                  | Method   | Closes the connection to the database.                                       |

### 7. API Layer
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| FastAPI app            | Object   | The main web server that handles requests from other programs.               |
| get_real_time_frame    | Function | Returns the latest thermal snapshot.                                         |
| add_zone               | Function | Lets users add a new zone via the web/API.                                   |
| delete_zone            | Function | Lets users remove a zone via the web/API.                                    |
| get_zone_average       | Function | Returns the average temperature for a zone.                                  |
| health                 | Function | Returns the current health status of the system.                             |

### API Endpoints Overview
| Method | Path                              | Purpose/Description                                 |
|--------|-----------------------------------|-----------------------------------------------------|
| GET    | /api/v1/thermal/real-time         | Get the latest thermal snapshot (768 values).        |
| GET    | /api/v1/zones                     | List all defined zones (with name and color).        |
| POST   | /api/v1/zones                     | Create a new zone (provide id, x, y, width, height, name, color). |
| DELETE | /api/v1/zones/{zone_id}           | Remove a zone by its ID.                            |
| GET    | /api/v1/zones/{zone_id}/average   | Get the average temperature for a specific zone.     |
| GET    | /api/v1/health                    | Get the current health status of the system.         |

**How to Access:**
- All endpoints are available via HTTP (typically from a web dashboard, script, or tool like curl/Postman).
- For GET requests, simply visit the URL or use a tool to fetch the data.
- For POST/DELETE, send a JSON payload (for POST) or specify the zone ID in the URL (for DELETE/average).
- Example: To add a zone, send a POST request to `/api/v1/zones` with a JSON body containing the zone details.

### 8. System Health Monitoring
| Name                   | Type     | What It Does                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| SystemMonitor          | Class    | Checks if all parts of the system are working correctly.                     |
| check_sensor_health    | Method   | Checks if the sensor is working.                                             |
| check_database_health  | Method   | Checks if the database is working.                                           |
| check_frame_buffer_health| Method | Checks if the frame buffer is working.                                       |
| check_alarm_system_health| Method | Checks if the alarm system is working.                                       |
| health_report          | Method   | Combines all health checks into one report.                                  |

---

This appendix should help you quickly find what each part of the code does, in plain language.
