import sqlite3
from datetime import datetime

db = "../database/database.db"

search_query = """
SELECT sb1.train_id, sb1.departure_time, sb2.arrival_time
FROM stopped_by sb1
JOIN stopped_by sb2 ON sb1.train_id = sb2.train_id
JOIN station s1 ON sb1.station_id = s1.station_id
JOIN station s2 ON sb2.station_id = s2.station_id
WHERE s1.station_name = ?
  AND s2.station_name = ?
  AND sb1.departure_time BETWEEN ? AND ?
ORDER BY sb1.departure_time;
"""

def train_query(departure, destination, date, time1, time2):
    try: 
        datetime1 = datetime.strptime(date + ' ' + time1, '%Y-%m-%d %H:%M:%S')
        datetime2 = datetime.strptime(date + ' ' + time2, '%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(search_query, (departure, destination, datetime1, datetime2))
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print("SQL error: ", e)
        return None
    finally:
        if conn:
            conn.close()