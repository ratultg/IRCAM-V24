"""
Unit tests for ZonesManager.
"""
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.src.zones import ZonesManager

def test_add_and_get_zones():
    zm = ZonesManager()
    zm.add_zone(1, 0, 0, 4, 4, name="Zone A", color="#123456")
    zm.add_zone(2, 5, 5, 3, 3, name="Zone B", color="#654321")
    zones = zm.get_zones()
    assert len(zones) == 2
    assert zones[0].id == 1
    assert zones[0].name == "Zone A"
    assert zones[0].color == "#123456"
    assert zones[1].id == 2
    assert zones[1].name == "Zone B"
    assert zones[1].color == "#654321"

def test_add_zone_limit():
    zm = ZonesManager()
    zm.add_zone(1, 0, 0, 4, 4, name="Zone A", color="#123456")
    zm.add_zone(2, 5, 5, 3, 3, name="Zone B", color="#654321")
    with pytest.raises(ValueError):
        zm.add_zone(3, 10, 10, 2, 2, name="Zone C", color="#abcdef")

def test_remove_zone():
    zm = ZonesManager()
    zm.add_zone(1, 0, 0, 4, 4, name="Zone A", color="#123456")
    zm.remove_zone(1)
    assert len(zm.get_zones()) == 0
    with pytest.raises(ValueError):
        zm.remove_zone(1)

def test_compute_zone_average():
    zm = ZonesManager()
    zm.add_zone(1, 0, 0, 2, 2, name="Zone A", color="#123456")
    frame = [float(i) for i in range(32*24)]
    avg = zm.compute_zone_average(1, frame)
    # The top-left 2x2 zone: indices 0,1,32,33
    expected = (0+1+32+33)/4
    assert abs(avg - expected) < 1e-6
    with pytest.raises(ValueError):
        zm.compute_zone_average(99, frame)
