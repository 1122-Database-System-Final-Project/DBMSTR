import sqlite3
from flask import Flask, request, jsonify
import os
from . import seat_management as seat
from . import order_modification as om

# 設定資料庫路徑
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db')

def delete_order(order_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    # 查詢該刪除的座位
    cursor.execute('SELECT seat_id FROM `ticket` WHERE order_id = ?', (order_id,))
    seats = [seat[0] for seat in cursor.fetchall()]

    # 還原座位狀態
    seat.delete_seated_seat(seats)

    # 刪除車票
    cursor.execute('''
        DELETE FROM `ticket`
        WHERE order_id = ?
    ''', (order_id,))

    
    # 刪除訂單
    cursor.execute('''
        DELETE FROM `order` 
        WHERE order_id = ?
    ''', (order_id,))


    connection.commit()
    connection.close()

