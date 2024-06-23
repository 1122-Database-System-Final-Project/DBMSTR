import sqlite3
from flask import Flask, request, jsonify
import os


'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_order(id_no,order_id):
    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT o.order_id, o.train_id, o.departure, o.destination, o.depart_time, o.arrive_time, o.order_status,
           u.name, u.phone, u.email,o.pay_expire_date, t.ticket_type, COUNT(t.ticket_type) as ticket_count, SUM(t.price) as total_price
    FROM `order` o
    JOIN `user` u ON o.user_id = u.user_id
    JOIN `ticket` t ON o.order_id = t.order_id
    WHERE u.id_no = ? AND o.order_id = ?
    GROUP BY t.ticket_type
    """
    cur.execute(query, (id_no, order_id))
    rows = cur.fetchall()
    conn.close()
    
    if rows:
        order_details = {
            "order_id": rows[0]["order_id"],
            "train_id": rows[0]["train_id"],
            "departure": rows[0]["departure"],
            "destination": rows[0]["destination"],
            "depart_time": rows[0]["depart_time"],
            "arrive_time": rows[0]["arrive_time"],
            "order_status": rows[0]["order_status"],
            "pay_expire_date": rows[0]["pay_expire_date"],
            "name": rows[0]["name"],
            "phone": rows[0]["phone"],
            "email": rows[0]["email"],
            "tickets": [],
            "total_price": 0,
            "total_tickets": 0
        }

        total_price = 0
        total_tickets = 0
        for row in rows:
            ticket_details = {
                "ticket_type": row["ticket_type"],
                "ticket_count": row["ticket_count"]
            }
            order_details["tickets"].append(ticket_details)
            total_price += row["total_price"]
            total_tickets += row["ticket_count"]
        
        order_details["total_price"] = total_price
        order_details["total_tickets"] = total_tickets

        return order_details
    else:
        return None

