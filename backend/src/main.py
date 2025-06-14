from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import os
os.environ['MOCK_SENSOR'] = '1'
from backend.src.sensor import ThermalSensor, MockThermalSensor
from backend.src.zones import ZonesManager
from backend.src.database import Database
from backend.src.alarms import AlarmManager
from backend.src.frames import compute_heatmap, compute_trend, detect_anomalies
import sys
import argparse
from functools import lru_cache
import logging
import csv

load_dotenv()

app = FastAPI(title="IR Thermal Monitoring API", version="1.0")

# --- Argument Parsing ---
def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mocksensor', action='store_true', help='Use mock sensor with random data')
    return parser.parse_known_args()

args, _ = parse_args()

# --- Database and Managers ---
def get_db() -> Database:
    db = Database()
    db.connect()
    return db

def get_zones_manager(db: Database = Depends(get_db)) -> ZonesManager:
    return ZonesManager(db)

def get_alarm_manager(db: Database = Depends(get_db)) -> AlarmManager:
    return AlarmManager(db)

# --- Pydantic Models ---
class ZoneRequest(BaseModel):
    id: int
    x: int
    y: int
    width: int
    height: int
    name: Optional[str] = None
    color: Optional[str] = None
    enabled: Optional[bool] = True
    threshold: Optional[float] = None

class ZoneResponse(BaseModel):
    id: int
    x: int
    y: int
    width: int
    height: int
    name: str
    color: str
    enabled: bool
    threshold: Optional[float]

class ThermalFrameResponse(BaseModel):
    timestamp: str
    frame: List[float]

class ZoneAverageResponse(BaseModel):
    zone_id: int
    average: float

class NotificationRequest(BaseModel):
    name: str
    type: str  # 'email', 'webhook', 'sms'
    config: str  # JSON-encoded config
    enabled: Optional[bool] = True

class NotificationResponse(BaseModel):
    id: int
    name: str
    type: str
    config: str
    enabled: bool
    created_at: str

class EventFrameResponse(BaseModel):
    id: int
    event_id: int
    timestamp: str
    frame_size: int
    # frame: bytes  # Not included in list, only for PNG download

class SettingsRequest(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingsResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class HeatmapRequest(BaseModel):
    start_time: str
    end_time: str
    zone_id: Optional[int] = None

class HeatmapResponse(BaseModel):
    heatmap: list[list[float]]
    width: int
    height: int
    start_time: str
    end_time: str
    zone_id: Optional[int] = None

class TrendRequest(BaseModel):
    start_time: str
    end_time: str
    zone_id: Optional[int] = None

class TrendResponse(BaseModel):
    timestamps: list[str]
    values: list[float]
    zone_id: Optional[int] = None

class AnomalyRequest(BaseModel):
    start_time: str
    end_time: str
    zone_id: Optional[int] = None

class AnomalyResponse(BaseModel):
    anomalies: list[dict]
    zone_id: Optional[int] = None

class ReportResponse(BaseModel):
    report_type: str
    start_time: str
    end_time: str
    zone_id: Optional[int] = None
    summary: dict

class AlarmEventResponse(BaseModel):
    alarm_id: int
    zone_id: int
    temperature: float
    timestamp: str
    event_type: str
    acknowledged: bool
    acknowledged_at: Optional[str] = None

class AlarmAcknowledgeRequest(BaseModel):
    alarm_id: int

# --- In-memory managers (replace with DB-backed in production) ---
@lru_cache()
def get_sensor_singleton() -> ThermalSensor | MockThermalSensor:
    if os.getenv('MOCK_SENSOR', '0') == '1':
        return MockThermalSensor()
    else:
        return ThermalSensor()

def get_sensor() -> ThermalSensor | MockThermalSensor:
    return get_sensor_singleton()

# --- API Endpoints ---
@app.get("/api/v1/thermal/real-time", response_model=ThermalFrameResponse)
def get_real_time_frame(sensor: ThermalSensor | MockThermalSensor = Depends(get_sensor)) -> ThermalFrameResponse:
    try:
        frame = sensor.read_frame()
        from datetime import datetime
        return ThermalFrameResponse(timestamp=datetime.utcnow().isoformat(), frame=frame)
    except Exception as e:
        logging.exception("Error in get_real_time_frame")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/zones", response_model=List[ZoneResponse])
def get_zones(zones_manager: ZonesManager = Depends(get_zones_manager)) -> list[ZoneResponse]:
    try:
        return [ZoneResponse(id=z.id, x=z.x, y=z.y, width=z.width, height=z.height, name=z.name, color=z.color, enabled=z.enabled, threshold=z.threshold) for z in zones_manager.get_zones()]
    except Exception as e:
        logging.exception("Error in get_zones")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/zones", response_model=ZoneResponse)
def add_zone(zone: ZoneRequest, zones_manager: ZonesManager = Depends(get_zones_manager)) -> ZoneResponse:
    try:
        enabled = zone.enabled if zone.enabled is not None else True
        zones_manager.add_zone(zone_id=zone.id, x=zone.x, y=zone.y, width=zone.width, height=zone.height, name=zone.name, color=zone.color, enabled=enabled, threshold=zone.threshold)
        return ZoneResponse(id=zone.id, x=zone.x, y=zone.y, width=zone.width, height=zone.height, name=zone.name or f"Zone ({zone.x},{zone.y})", color=zone.color or "#FF0000", enabled=enabled, threshold=zone.threshold)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logging.exception("Error in add_zone")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/zones/{zone_id}")
def delete_zone(zone_id: int, zones_manager: ZonesManager = Depends(get_zones_manager)) -> dict[str, str]:
    try:
        zones_manager.remove_zone(zone_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logging.exception("Error in delete_zone")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/zones/{zone_id}/average", response_model=ZoneAverageResponse)
def get_zone_average(zone_id: int, zones_manager: ZonesManager = Depends(get_zones_manager), sensor: ThermalSensor | MockThermalSensor = Depends(get_sensor)) -> ZoneAverageResponse:
    try:
        frame = sensor.read_frame()
        avg = zones_manager.compute_zone_average(zone_id, frame)
        return ZoneAverageResponse(zone_id=zone_id, average=avg)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logging.exception("Error in get_zone_average")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/api/v1/notifications/settings", response_model=List[NotificationResponse])
def get_notifications(alarm_manager: AlarmManager = Depends(get_alarm_manager)):
    try:
        return [NotificationResponse(**n) for n in alarm_manager.get_notifications()]
    except Exception as e:
        logging.exception("Error in get_notifications")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notifications/settings", response_model=NotificationResponse)
def add_notification(notification: NotificationRequest, alarm_manager: AlarmManager = Depends(get_alarm_manager)):
    try:
        notification_id = alarm_manager.add_notification(
            notification.name, notification.type, notification.config, notification.enabled if notification.enabled is not None else True
        )
        n = alarm_manager.get_notifications()
        n = next((item for item in n if item["id"] == notification_id), None)
        if not n:
            raise HTTPException(status_code=500, detail="Failed to add notification")
        return NotificationResponse(**n)
    except Exception as e:
        logging.exception("Error in add_notification")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/notifications/settings/{notification_id}", response_model=None)
def update_notification(notification_id: int, notification: NotificationRequest, alarm_manager: AlarmManager = Depends(get_alarm_manager)):
    try:
        alarm_manager.update_notification(notification_id, notification.name, notification.type, notification.config, notification.enabled if notification.enabled is not None else True)
    except Exception as e:
        logging.exception("Error in update_notification")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/notifications/settings/{notification_id}", response_model=None)
def delete_notification(notification_id: int, alarm_manager: AlarmManager = Depends(get_alarm_manager)):
    try:
        alarm_manager.delete_notification(notification_id)
    except Exception as e:
        logging.exception("Error in delete_notification")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/{event_id}/frames", response_model=List[EventFrameResponse])
def get_event_frames(event_id: int, db: Database = Depends(get_db)):
    try:
        cur = db.execute_query(
            "SELECT id, event_id, timestamp, frame_size FROM thermal_frames WHERE event_id = ? ORDER BY timestamp ASC",
            (event_id,)
        )
        frames = [
            EventFrameResponse(
                id=row[0], event_id=row[1], timestamp=row[2], frame_size=row[3]
            )
            for row in cur.fetchall()
        ]
        return frames
    except Exception as e:
        logging.exception("Error in get_event_frames")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse, Response, JSONResponse
import io
from PIL import Image
import numpy as np

@app.get("/api/v1/events/{event_id}/frames.png")
def download_event_frames_png(event_id: int, db: Database = Depends(get_db)):
    try:
        cur = db.execute_query(
            "SELECT frame FROM thermal_frames WHERE event_id = ? ORDER BY timestamp ASC",
            (event_id,)
        )
        frames = [row[0] for row in cur.fetchall()]
        if not frames:
            raise HTTPException(status_code=404, detail="No frames found for event")
        # For demo: stack frames vertically as grayscale PNG
        images = []
        for frame_bytes in frames:
            arr = np.frombuffer(frame_bytes, dtype=np.float32)
            if arr.size == 32*24:
                arr = arr.reshape((24,32))
                arr = ((arr - arr.min()) / (np.ptp(arr) or 1) * 255).astype(np.uint8)
                img = Image.fromarray(arr, mode="L")
                images.append(img)
        if not images:
            raise HTTPException(status_code=500, detail="No valid frames to render")
        # Stack vertically
        total_height = sum(img.height for img in images)
        out_img = Image.new("L", (images[0].width, total_height))
        y = 0
        for img in images:
            out_img.paste(img, (0, y))
            y += img.height
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        logging.exception("Error in download_event_frames_png")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/{event_id}/frames/blobs")
def get_event_frame_blobs(event_id: int, db: Database = Depends(get_db)):
    """
    Returns all frames for an event as a list of dicts:
    [{
        "id": int,
        "event_id": int,
        "timestamp": str,
        "frame_size": int,
        "frame": base64-encoded float32 array (32x24, row-major)
    }, ...]
    Frame format: 32x24 float32, row-major, base64-encoded for transport.
    """
    import base64
    try:
        cur = db.execute_query(
            "SELECT id, event_id, timestamp, frame_size, frame FROM thermal_frames WHERE event_id = ? ORDER BY timestamp ASC",
            (event_id,)
        )
        frames = []
        for row in cur.fetchall():
            frame_b64 = base64.b64encode(row[4]).decode("ascii")
            frames.append({
                "id": row[0],
                "event_id": row[1],
                "timestamp": row[2],
                "frame_size": row[3],
                "frame": frame_b64
            })
        return JSONResponse(content=frames)
    except Exception as e:
        logging.exception("Error in get_event_frame_blobs")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/frames/export")
def export_frames(event_id: Optional[int] = None, overlay: Optional[str] = None, db: Database = Depends(get_db)):
    try:
        query = "SELECT id, event_id, timestamp, frame_size, frame FROM thermal_frames"
        params = ()
        if event_id is not None:
            query += " WHERE event_id = ?"
            params = (event_id,)
        cur = db.execute_query(query, params)
        frames = cur.fetchall()
        if not frames:
            raise HTTPException(status_code=404, detail="No frames found")
        import io, csv
        output = io.StringIO()
        writer = csv.writer(output)
        base_cols = ["id", "event_id", "timestamp", "frame_size"]
        stat_cols = ["mean", "min", "max", "std"] if overlay == "stats" else []
        writer.writerow(base_cols + stat_cols)
        from backend.src.frames import get_frame_stats
        for row in frames:
            base = list(row[:4])
            if overlay == "stats":
                stats = get_frame_stats(row[4])
                writer.writerow(base + [stats[c] for c in stat_cols])
            else:
                writer.writerow(base)
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=frames.csv"})
    except Exception as e:
        logging.exception("Error in export_frames")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/settings", response_model=List[SettingsResponse])
def get_settings(db: Database = Depends(get_db)):
    try:
        settings = db.list_settings()
        return [SettingsResponse(**s) for s in settings]
    except Exception as e:
        logging.exception("Error in get_settings")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/settings", response_model=SettingsResponse)
def set_setting(setting: SettingsRequest, db: Database = Depends(get_db)):
    try:
        db.set_setting(setting.key, setting.value, setting.description)
        s = db.get_setting(setting.key)
        if not s:
            raise HTTPException(status_code=500, detail="Failed to set setting")
        return SettingsResponse(**s)
    except Exception as e:
        logging.exception("Error in set_setting")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/database/backup")
def backup_database(db: Database = Depends(get_db)):
    try:
        def file_iterator():
            with open(db.db_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        return StreamingResponse(file_iterator(), media_type="application/octet-stream", headers={"Content-Disposition": "attachment; filename=ir_monitoring_backup.db"})
    except Exception as e:
        logging.exception("Error in backup_database")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/database/restore")
def restore_database(file: UploadFile = File(...), db: Database = Depends(get_db)):
    try:
        temp_path = "restore_temp.db"
        with open(temp_path, "wb") as f:
            f.write(file.file.read())
        db.restore(temp_path)
        return {"status": "restored"}
    except Exception as e:
        logging.exception("Error in restore_database")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/database/migrate")
def migrate_database(db: Database = Depends(get_db)):
    try:
        db.migrate()
        return {"status": "migrated"}
    except Exception as e:
        logging.exception("Error in migrate_database")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/heatmap", response_model=HeatmapResponse)
def get_heatmap(start_time: str, end_time: str, zone_id: Optional[int] = None, db: Database = Depends(get_db)):
    # Fetch data
    data = db.get_thermal_data(start_time, end_time, zone_id)
    # Use default grid size or zone grid
    if zone_id:
        grid = db.get_zone_grid(zone_id)
        width, height = grid.get("width", 32), grid.get("height", 24)
    else:
        width, height = 32, 24
    heatmap = compute_heatmap(data, width, height)
    return HeatmapResponse(heatmap=heatmap, width=width, height=height, start_time=start_time, end_time=end_time, zone_id=zone_id)

@app.get("/api/v1/analytics/trends", response_model=TrendResponse)
def get_trends(start_time: str, end_time: str, zone_id: Optional[int] = None, db: Database = Depends(get_db)):
    data = db.get_thermal_data(start_time, end_time, zone_id)
    timestamps, values = compute_trend(data)
    return TrendResponse(timestamps=timestamps, values=values, zone_id=zone_id)

@app.get("/api/v1/analytics/anomalies", response_model=AnomalyResponse)
def get_anomalies(start_time: str, end_time: str, zone_id: Optional[int] = None, db: Database = Depends(get_db)):
    data = db.get_thermal_data(start_time, end_time, zone_id)
    anomalies = detect_anomalies(data)
    return AnomalyResponse(anomalies=anomalies, zone_id=zone_id)

@app.get("/api/v1/reports", response_model=ReportResponse)
def get_report(report_type: str, start_time: str, end_time: str, zone_id: Optional[int] = None, db: Database = Depends(get_db)):
    # For now, support 'summary' (mean/min/max), 'trend', 'anomaly_count'
    data = db.get_thermal_data(start_time, end_time, zone_id)
    summary = {}
    if report_type == "summary":
        temps = [d["temperature"] for d in data]
        summary = {
            "count": len(temps),
            "mean": float(np.mean(temps)) if temps else 0.0,
            "min": float(np.min(temps)) if temps else 0.0,
            "max": float(np.max(temps)) if temps else 0.0,
        }
    elif report_type == "trend":
        from backend.src.frames import compute_trend
        ts, vals = compute_trend(data)
        summary = {"timestamps": ts, "values": vals}
    elif report_type == "anomaly_count":
        from backend.src.frames import detect_anomalies
        anomalies = detect_anomalies(data)
        summary = {"anomaly_count": len(anomalies)}
    else:
        raise HTTPException(status_code=400, detail="Unknown report_type")
    return ReportResponse(report_type=report_type, start_time=start_time, end_time=end_time, zone_id=zone_id, summary=summary)

@app.get("/api/v1/alarms/history", response_model=List[AlarmEventResponse])
def get_alarm_history(db: Database = Depends(get_db)):
    try:
        cur = db.execute_query("""
            SELECT ae.id, ae.zone_id, ae.temperature, ae.timestamp, ae.alarm_id, a.acknowledged, a.acknowledged_at
            FROM alarm_events ae
            LEFT JOIN alarms a ON ae.alarm_id = a.id
            ORDER BY ae.timestamp DESC LIMIT 100
        """)
        events = [
            AlarmEventResponse(
                alarm_id=row[4],
                zone_id=row[1],
                temperature=row[2],
                timestamp=row[3],
                event_type="threshold",
                acknowledged=bool(row[5]) if len(row) > 5 and row[5] is not None else False,
                acknowledged_at=row[6] if len(row) > 6 else None
            )
            for row in cur.fetchall()
        ]
        return events
    except Exception as e:
        logging.exception("Error in get_alarm_history")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/alarms/acknowledge")
def acknowledge_alarm(req: AlarmAcknowledgeRequest, alarm_manager: AlarmManager = Depends(get_alarm_manager)):
    try:
        alarm_manager.acknowledge_alarm(req.alarm_id)
        return {"status": "acknowledged", "alarm_id": req.alarm_id}
    except Exception as e:
        logging.exception("Error in acknowledge_alarm")
        raise HTTPException(status_code=500, detail=str(e))