import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
Unit tests for ThermalSensor (MLX90640) handler.
"""
import pytest
import logging
from backend.src.sensor import ThermalSensor

class DummyMLX90640:
    def __init__(self, i2c, address=0x33):
        self.i2c = i2c
        self.address = address
        self.refresh_rate = 2
        self.fail_count = 0
    def getFrame(self, frame):
        if self.fail_count > 0:
            self.fail_count -= 1
            raise IOError("Simulated I2C error")
        for i in range(768):
            frame[i] = float(i)

class DummyI2C:
    pass

def test_read_frame_success(monkeypatch):
    monkeypatch.setattr("backend.src.sensor.MLX90640", DummyMLX90640)
    monkeypatch.setattr("backend.src.sensor.busio", type("busio", (), {"I2C": lambda scl, sda: DummyI2C()}) )
    sensor = ThermalSensor()
    frame = sensor.read_frame()
    assert len(frame) == 768
    assert frame[0] == 0.0
    assert frame[-1] == 767.0

def test_read_frame_retry(monkeypatch):
    monkeypatch.setattr("backend.src.sensor.MLX90640", DummyMLX90640)
    monkeypatch.setattr("backend.src.sensor.busio", type("busio", (), {"I2C": lambda scl, sda: DummyI2C()}) )
    sensor = ThermalSensor()
    sensor.sensor.fail_count = 2
    frame = sensor.read_frame()
    assert len(frame) == 768

def test_read_frame_fail(monkeypatch):
    monkeypatch.setattr("backend.src.sensor.MLX90640", DummyMLX90640)
    monkeypatch.setattr("backend.src.sensor.busio", type("busio", (), {"I2C": lambda scl, sda: DummyI2C()}) )
    sensor = ThermalSensor(max_retries=1)
    sensor.sensor.fail_count = 5
    with pytest.raises(IOError):
        sensor.read_frame()
