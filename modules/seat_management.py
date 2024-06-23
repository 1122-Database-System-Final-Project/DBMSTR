import sqlite3
import os
from datetime import datetime

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db') # 導航到目錄位置

# 獲取指定班次的所有空座位
def get_all_available_seats_by_train_id(train_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''
                   SELECT seat.seat_id, seat.seat_type, seat.car_id 
                   FROM seat
                   WHERE (seat.seat_id/1000) = ? AND trim(seat.occupied) = 'n'
                   ''', (train_id,))
    seats = cursor.fetchall()
    connection.close()
    return seats

#更新訂的座位
# seats = ['511101', '511102']
def update_seat_be_seated(seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for seat in seats:
        cursor.execute('''
            UPDATE seat 
            SET occupied = 'y' 
            WHERE seat_id = ?
            ''', (seat,))
    connection.commit()  
    connection.close()
        
#刪除先前訂的座位
def delete_seated_seat(seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for seat in seats:
        cursor.execute('''
            UPDATE seat 
            SET occupied = 'n'
            WHERE seat_id = ?
            ''', (seat,))
    connection.commit() 
    connection.close()
