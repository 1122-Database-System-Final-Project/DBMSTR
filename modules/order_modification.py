import sqlite3
import os
from flask import Flask, request, jsonify

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))  # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db')  # 導航到目錄位置

# 更新訂單座位
def update_order_seats(order_id, new_seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # 查詢訂單原本的座位
    cursor.execute('SELECT seat_id FROM booking WHERE order_id = ?', (order_id,))
    original_seats = cursor.fetchall()

    # 更新新座位為已訂
    for seat_id in new_seats:
        cursor.execute('UPDATE seats SET is_available = 0 WHERE id = ?', (seat_id,))
    
    # 更新原座位為空
    for seat_id in original_seats:
        cursor.execute('UPDATE seats SET is_available = 1 WHERE id = ?,', (seat_id,))
    
    # 更新訂單中的座位
    cursor.execute('DELETE FROM booking WHERE order_id = ?', (order_id,))
    for seat_id in new_seats:
        cursor.execute('INSERT INTO booking (order_id, seat_id) VALUES (?, ?)', (order_id, seat_id))
    
    connection.commit()
    connection.close()
