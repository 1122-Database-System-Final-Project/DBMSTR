import sqlite3
from datetime import datetime

db = "../database/database.db"

search_query = """
SELECT sb1.train_id, sb1.departure_time, sb2.arrival_time
FROM stopped_by sb1
JOIN stopped_by sb2 ON sb1.train_id = sb2.train_id
JOIN station s1 ON sb1.station_id = s1.station_id
JOIN station s2 ON sb2.station_id = s2.station_id
WHERE trim(s1.station_name) = ?
  AND trim(s2.station_name) = ?
  AND trim(sb1.departure_time) BETWEEN ? AND ?
  AND trim(sb2.arrival_time) > trim(sb1.departure_time)
ORDER BY trim(sb1.departure_time);
"""

def get_stations():
    try: 
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT station_name FROM station;")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except sqlite3.Error as e:
        print("SQL error: ", e)
        return None

def train_query(departure, destination, time1, time2):
    try: 
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(search_query, (departure, destination, time1, time2))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except sqlite3.Error as e:
        print("SQL error: ", e)
        return None