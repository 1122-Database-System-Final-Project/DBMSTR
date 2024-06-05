import sqlite3
import os
from datetime import datetime

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db') # 導航到目錄位置

# 獲取指定班次的所有空座位
def get_all_available_seats_by_train_id(train_id, counting):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''
                   SELECT * 
                   FROM seats 
                   WHERE train_id = ? AND is_available = 1
                   ''', (train_id, counting))
    seats = cursor.fetchall()
    connection.close()
    return seats

#更新訂的座位
def update_seat_be_seated(seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for seat_id in seats:
        cursor.execute('''
            UPDATE seats 
            SET is_available = 0 
            WHERE id = ?
            ''', (seat_id,))
        
#刪除先前訂的座位
def delete_seated_seat(seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for seat_id in seats:
        cursor.execute('''
            UPDATE seats 
            SET is_available = 1 
            WHERE id = ?
            ''', (seat_id,))
