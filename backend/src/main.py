from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import os
from backend.src.sensor import ThermalSensor, MockThermalSensor
from backend.src.zones import ZonesManager
import sys
import argparse

load_dotenv()

app = FastAPI(title="IR Thermal Monitoring API", version="1.0")

# --- Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mocksensor', action='store_true', help='Use mock sensor with random data')
    return parser.parse_known_args()

args, _ = parse_args()

# --- Pydantic Models ---
class ZoneRequest(BaseModel):
    id: int
    x: int
    y: int
    width: int
    height: int
    name: Optional[str] = None
    color: Optional[str] = None

class ZoneResponse(BaseModel):
    id: int
    x: int
    y: int
    width: int
    height: int
    name: str
    color: str

class ThermalFrameResponse(BaseModel):
    timestamp: str
    frame: List[float]

class ZoneAverageResponse(BaseModel):
    zone_id: int
    average: float

# --- In-memory managers (replace with DB-backed in production) ---
zones_manager = ZonesManager()
_sensor_instance = None

def get_sensor():
    global _sensor_instance
    if _sensor_instance is None:
        if os.getenv('MOCK_SENSOR', '0') == '1':
            _sensor_instance = MockThermalSensor()
        else:
            _sensor_instance = ThermalSensor()
    return _sensor_instance

# --- API Endpoints ---
@app.get("/api/v1/thermal/real-time", response_model=ThermalFrameResponse)
def get_real_time_frame():
    frame = get_sensor().read_frame()
    # In production, add timestamp from RTC or system clock
    from datetime import datetime
    return ThermalFrameResponse(timestamp=datetime.utcnow().isoformat(), frame=frame)

@app.get("/api/v1/zones", response_model=List[ZoneResponse])
def get_zones():
    return [ZoneResponse(id=z.id, x=z.x, y=z.y, width=z.width, height=z.height, name=z.name, color=z.color) for z in zones_manager.get_zones()]

@app.post("/api/v1/zones", response_model=ZoneResponse)
def add_zone(zone: ZoneRequest):
    try:
        zones_manager.add_zone(zone_id=zone.id, x=zone.x, y=zone.y, width=zone.width, height=zone.height, name=zone.name, color=zone.color)
        return ZoneResponse(id=zone.id, x=zone.x, y=zone.y, width=zone.width, height=zone.height, name=zone.name or f"Zone ({zone.x},{zone.y})", color=zone.color or "#FF0000")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/zones/{zone_id}")
def delete_zone(zone_id: int):
    try:
        zones_manager.remove_zone(zone_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v1/zones/{zone_id}/average", response_model=ZoneAverageResponse)
def get_zone_average(zone_id: int):
    frame = get_sensor().read_frame()
    try:
        avg = zones_manager.compute_zone_average(zone_id, frame)
        return ZoneAverageResponse(zone_id=zone_id, average=avg)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}