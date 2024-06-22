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
    seats = cursor.fetchall()
    print(f"Seats to delete: {seats}")
    # 查詢該刪除的車廂
    #cursor.execute('SELECT car_id FROM ticket WHERE order_id = ?', (order_id,))
    #car = cursor.fetchall()


    # 還原座位狀態
    seat.delete_seated_seat(seats)
    


    # 刪除車票
    cursor.execute('''
        DELETE FROM `ticket`
        WHERE order_id = ?
    ''', (order_id,))
    print(f"Deleted tickets for order_id: {order_id}")

    
    # 确认删除的车票
    cursor.execute('SELECT * FROM `ticket` WHERE order_id = ?', (order_id,))
    remaining_tickets = cursor.fetchall()
    print(f"Remaining tickets after deletion: {remaining_tickets}")
    


    # 刪除訂單
    cursor.execute('''
        DELETE FROM `order` 
        WHERE order_id = ?
    ''', (order_id,))

    print(f"Deleted order with order_id: {order_id}")

    # 确认删除的订单
    cursor.execute('SELECT * FROM `order` WHERE order_id = ?', (order_id,))
    remaining_orders = cursor.fetchall()
    print(f"Remaining orders after deletion: {remaining_orders}")

    connection.commit()
    connection.close()

