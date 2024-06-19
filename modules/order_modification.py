import sqlite3
import os
import modules.seat_management as seat
import modules.order_query as oq
from flask import Flask, request, jsonify

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))  # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db')  # 導航到目錄位置

# 更新訂單座位
def change_my_seat(order_id,train_id,new_seats):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # 查詢訂單原本的座位
    cursor.execute('SELECT seat_id FROM ticket WHERE order_id = ?', (order_id,))
    original_seats = cursor.fetchall()
    
    # 更新新座位
    seat.update_seat_be_seated(train_id, new_seats)

    # 刪除原本座位
    seat.delete_seated_seat(train_id, original_seats)

    connection.commit()
    connection.close()