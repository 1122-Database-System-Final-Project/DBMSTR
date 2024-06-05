import sqlite3
import os
from datetime import datetime
import seat_management as seat

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db') # 導航到目錄位置

# 獲取所有班次以供選擇
def get_all_trains(start_time, end_time, start_station, end_station, counting, ticket_type):
    
    # 如果資料不完整則不能查詢
    if not (start_time and end_time and start_station and end_station and counting and ticket_type):
        return {"status": "error", "message": "All fields are required"}

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    query = """
    SELECT * FROM train_schedule 
    WHERE departure_time >= ? 
    AND departure_time <= ? 
    AND start_station = ? 
    AND end_station = ? 
    AND available_tickets >= ? 
    AND ticket_type = ?
    """
    params = [start_time, end_time, start_station, end_station, counting, ticket_type]
    
    cursor.execute(query, params)
    trains = cursor.fetchall()
    connection.close()
    
    # 回傳資料且回報成功
    return {"status": "success", "data": trains}

def book_seat(train_id, seats, passenger_info):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:
        # 根據票的數量檢查座位是否可用
        for seat_id in seats:
            cursor.execute('''
                        SELECT is_available 
                        FROM seats 
                        WHERE id = ? AND train_id = ?
                        ''', (seat_id, train_id))
            seat = cursor.fetchone() # 取得可用座位
            if seat is None or seat[0] == 0:
                raise Exception("Seat is not available")
        
        # 更新座位狀態
        seat.update_seat_be_seated(seats)

        # 新增訂單
        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for seat_id in seats:
            cursor.execute('''
                        INSERT INTO bookings (train_id, seat_id, passenger_info, booking_time) 
                        VALUES (?, ?, ?, ?)
                        ''', (train_id, seat_id, passenger_info, booking_time))
        
        connection.commit()
        return {"status": "success", "message": "Booking successful"}
    
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        connection.close()
