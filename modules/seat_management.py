import sqlite3
import os
from datetime import datetime

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db') # 導航到目錄位置

# 獲取指定班次的所有空座位
def get_all_available_seats_by_train_id(train_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    query = '''
    SELECT s.car_id, s.seat_id
    FROM seat s
    JOIN car c ON s.car_id = c.car_id
    JOIN train t ON c.train_id = t.train_id
    WHERE t.train_id = ? -- 指定的班次
        AND s.occupied = 0
    '''
    cursor.execute(query, (train_id))
    # seats 會包含 car_id, seat_id
    seats = cursor.fetchall()
    connection.close()
    return seats

# 給定車次, 車廂號碼, 座位號碼, 更新訂的座位(一個一個處理)
def update_seat_be_seated(train_id, car_id, seat_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE seat s
        JOIN car c ON s.car_id = c.car_id
        JOIN train t ON c.train_id = t.train_id
        SET s.occupied = 1 -- 更新成被佔用
        WHERE t.train_id = ?
            AND c.car_id = ?
            AND s.seat_id = ?
        ''', (train_id, car_id, seat_id))
    connection.commit()  
    connection.close()
        
# 給定車次, 車廂號碼, 座位號碼, 刪除先前訂的座位(一個一個處理)
def delete_seated_seat(train_id, car_id, seat_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE seat s
        JOIN car c ON s.car_id = c.car_id
        JOIN train t ON c.train_id = t.train_id
        SET s.occupied = 0 -- 取消被佔用
        WHERE t.train_id = ?
            AND c.car_id = ?
            AND s.seat_id = ?
        ''', (train_id, car_id, seat_id,))
    connection.commit() 
    connection.close()
