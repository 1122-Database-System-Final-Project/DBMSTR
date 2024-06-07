import sqlite3
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 設定資料庫路徑
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_order():
    id_no = request.args.get('id_no')
    order_id = request.args.get('order_id')

    if not id_no or not order_id:
        return jsonify({"error": "Missing id_no or order_id"}), 400

    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT o.order_id, o.train_id, o.departure, o.destination, o.depart_time, o.arrive_time, o.order_status,
           u.name, u.phone, u.email
    FROM `order` o
    JOIN `user` u ON o.user_id = u.user_id
    WHERE o.id_no = ? AND o.order_id = ?
    """

    cur.execute(query, (id_no, order_id))
    order = cur.fetchone()
    conn.close()
    
    if order:
        order_details = {
            "order_id": order["order_id"],
            "train_id": order["train_id"],
            "departure": order["departure"],
            "destination": order["destination"],
            "depart_time": order["depart_time"],
            "arrive_time": order["arrive_time"],
            "order_status": order["order_status"],
            "name": order["name"],
            "phone": order["phone"],
            "email": order["email"]
        }
        return jsonify(order_details), 200
    else:
        return jsonify({"error": "Order not found"}), 404

