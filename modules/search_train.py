import sqlite3
import os
from datetime import datetime

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
db = os.path.join(BASE_DIRECTORY, '../database/database.db')

search_query = """
SELECT sb1.train_id, train_type, sb1.departure_time, sb2.arrival_time, s1.station_name, s2.station_name
FROM stopped_by sb1
JOIN stopped_by sb2 ON sb1.train_id = sb2.train_id
JOIN station s1 ON sb1.station_id = s1.station_id
JOIN station s2 ON sb2.station_id = s2.station_id
JOIN train ON sb1.train_id = train.train_id
WHERE trim(s1.station_name) = ?
  AND trim(s2.station_name) = ?
  AND trim(sb1.departure_time) BETWEEN ? AND ?
  AND trim(sb2.arrival_time) > trim(sb1.departure_time)
ORDER BY trim(sb1.departure_time);
"""

def train_query(departure, destination, time1, time2):
    try: 
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(search_query, (departure, destination, time1, time2))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        if not result:
            result = [(000, 'No result', time1, time2, departure, destination)]
        return result
    except sqlite3.Error as e:
        result = [(000, '測試', '00:00:00', '00:00:00', 'SQL error', e)]
        return result