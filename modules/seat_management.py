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
    cursor.execute('''
                   SELECT seat.seat_id, seat.seat_type, seat.car_id 
                   FROM seat JOIN car ON seat.car_id = car.car_id
                   WHERE car.train_id = ? AND seat.occupied = 0
                   ''', (train_id))
    seats = cursor.fetchall()
    connection.close()
    return seats

#更新訂的座位
#seats會包含 car_id 和 seat_id
def update_seat_be_seated(train_id, seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for car_id, seat_id in seats:
        cursor.execute('''
            UPDATE seat 
            SET occupied = 1 
            WHERE seat_id = ? AND car_id IN (
                        SELECT car.car_id
                        FROM seat JOIN car ON seat.car_id = car.car_id
                        WHERE car.train_id = ? )
            ''', (train_id, car_id, seat_id,))
    connection.commit()  
    connection.close()
        
#刪除先前訂的座位
#seats會包含 car_id 和 seat_id
def delete_seated_seat(train_id, seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for car_id, seat_id in seats:
        cursor.execute('''
            UPDATE seat 
            SET occupied = 0
            WHERE seat_id = ? AND car_id IN (
                        SELECT car.car_id
                        FROM seat JOIN car ON seat.car_id = car.car_id
                        WHERE car.train_id = ? )
            ''', (train_id, car_id, seat_id,))
    connection.commit() 
    connection.close()
