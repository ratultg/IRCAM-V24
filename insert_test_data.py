import sqlite3
import numpy as np

conn = sqlite3.connect(r'd:/IRCAM V24/ir_monitoring.db')
cur = conn.cursor()

# Insert a test zone
cur.execute("INSERT INTO zones (x, y, width, height, name, color, enabled, threshold) VALUES (10, 10, 100, 100, 'Test Zone', '#00FF00', 1, 50.0)")
zone_id = cur.lastrowid

# Insert a test alarm event
cur.execute("INSERT INTO alarm_events (zone_id, timestamp, temperature, alarm_id) VALUES (?, datetime('now'), 55.0, 1)", (zone_id,))
event_id = cur.lastrowid

# Insert a test thermal_data row for analytics
cur.execute("INSERT INTO thermal_data (zone_id, timestamp, temperature) VALUES (?, datetime('now'), ?)", (zone_id, 55.0))
# Insert a valid 32x24 float32 frame
arr = (np.ones((24,32), dtype=np.float32) * 55.0).tobytes()
cur.execute("INSERT INTO thermal_frames (event_id, timestamp, frame, frame_size) VALUES (?, datetime('now'), ?, ?)", (event_id, sqlite3.Binary(arr), len(arr)))

conn.commit()
print('zone_id:', zone_id, 'event_id:', event_id)
conn.close()
