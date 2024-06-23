import sqlite3
import os
from . import seat_management as seat
from . import order_query as oq
from flask import Flask, request, jsonify

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))  # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db')  # 導航到目錄位置

def find_original_seat(order_id):
    connection = sqlite3.connect(DATABASE, timeout=20)
    cursor = connection.cursor()

    # 查詢訂單原本的座位
    cursor.execute('SELECT seat_id FROM ticket WHERE order_id = ?', (order_id,))
    original_seats = [seat[0] for seat in cursor.fetchall()]
    connection.commit()
    connection.close()
    
    return original_seats

# 更新訂單座位
def change_my_seat(order_id,new_seats):
    connection = sqlite3.connect(DATABASE, timeout=20)
    cursor = connection.cursor()

    # 查詢訂單原本的座位
    cursor.execute('SELECT seat_id FROM ticket WHERE order_id = ?', (order_id,))
    original_seats = [seat[0] for seat in cursor.fetchall()]

    #更改車票中的資訊
    for original_seat, new_seat in zip(original_seats, new_seats):
        new_car_id= new_seat// 100
        cursor.execute('''
            UPDATE ticket
            SET seat_id = ? ,car_id = ?
            WHERE order_id = ? AND seat_id = ?
        ''', (new_seat,new_car_id, order_id, original_seat))
    
    connection.commit()
    connection.close()