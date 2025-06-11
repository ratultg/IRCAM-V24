"""
sensor.py

MLX90640 sensor handler for IR Thermal Monitoring System.
"""
import time
import logging
from typing import List
import random

try:
    import smbus2
except ImportError:
    smbus2 = None
try:
    import board
    import busio
    from adafruit_mlx90640 import MLX90640
except ImportError:
    board = None
    busio = None
    MLX90640 = None


class ThermalSensor:
    """
    Handles MLX90640 thermal sensor readings via I2C (Adafruit driver).
    """
    def __init__(
        self,
        bus: int = 1,
        address: int = 0x33,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize I2C bus and sensor.

        Raises:
            RuntimeError: If required libraries are not installed or I2C bus cannot be opened.
        """
        if MLX90640 is None or board is None or busio is None:
            raise RuntimeError("Adafruit MLX90640 dependencies not installed; install via 'pip install adafruit-circuitpython-mlx90640'")
        self.bus_number = bus
        self.address = address
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        try:
            # On Raspberry Pi, use busio.I2C() with default pins (SCL=3, SDA=2)
            # If board.SCL/SDA are not available, use the GPIO numbers directly
            self.i2c = busio.I2C(scl=3, sda=2)
            self.sensor = MLX90640(self.i2c, address=self.address)
            self.sensor.refresh_rate = 2  # 2Hz
        except Exception as e:
            logging.error(f"Failed to initialize MLX90640: {e}")
            raise RuntimeError(f"Cannot initialize MLX90640 sensor: {e}")

    def read_frame(self) -> List[float]:
        """
        Read a thermal frame (768 temperature points) from the MLX90640 sensor.

        Returns:
            List[float]: List of 768 temperature readings (°C).

        Raises:
            IOError: If repeated I2C read failures occur.
        """
        retries = 0
        frame = [0] * 768  # Adafruit expects ints, will be filled with floats
        while retries <= self.max_retries:
            try:
                self.sensor.getFrame(frame)
                if len(frame) != 768:
                    raise ValueError("MLX90640 frame length incorrect")
                return [float(x) for x in frame]
            except Exception as e:
                logging.warning(f"Read frame attempt {retries + 1} failed: {e}")
                retries += 1
                time.sleep(self.backoff_factor * retries)
        logging.error("Exceeded max retries reading thermal frame")
        raise IOError("Failed to read thermal frame after retries")


class MockThermalSensor:
    """
    Mock sensor for development/testing. Generates random temperature frames with noise.
    """
    def __init__(self, base_temp: float = 25.0, noise: float = 2.0):
        self.base_temp = base_temp
        self.noise = noise

    def read_frame(self) -> List[float]:
        # Simulate 768 temperature readings with random noise
        return [
            random.gauss(self.base_temp, self.noise)
            for _ in range(768)
        ]
