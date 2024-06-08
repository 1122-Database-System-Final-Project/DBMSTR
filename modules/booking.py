import sqlite3
from flask import session
import os
import math
from datetime import datetime, timedelta
import seat_management

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/train_booking.db') # 導航到目錄位置

# 獲取所有班次以供選擇
def get_all_trains(start_time, end_time, departure, destination, counting, train_type):
    
    # 如果資料不完整則不能查詢
    if not (start_time and end_time and departure and destination and counting and train_type):
        return {"status": "error", "message": "All fields are required"}

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = """
    SELECT
        t.train_id,
        sb1.departure_time AS train_departure_time, -- 出發時間
        sb2.arrival_time AS train_arrival_time, -- 抵達時間
        s1.station_name AS departure_station, -- 出發車站
        s2.station_name AS arrival_station, -- 抵達車站
        COUNT(seat.seat_id) AS available_seats -- 剩餘座位數
    FROM train t
    JOIN stopped_by sb1 ON t.train_id = sb1.train_id
    JOIN stopped_by sb2 ON t.train_id = sb2.train_id
    JOIN station s1 ON sb1.station_id = s1.station_id
    JOIN station s2 ON sb2.station_id = s2.station_id
    JOIN car ON t.train_id = car.train_id
    JOIN seat ON car.car_id = seat.car_id
    WHERE t.train_type = ? -- 火車類型
        AND s1.station_name = ? -- 出發車站
        AND s2.station_name = ? -- 目標車站
        AND sb1.departure_time >= ? -- 開始時間
        AND sb1.departure_time <= ? -- 結束時間
        AND sb1.arrival_time < sb2.departure_time
        AND seat.occupied = 0 -- 車位沒有被佔用
    GROUP BY t.train_id, sb1.departure_time, sb2.arrival_time, s1.station_name, s2.station_name
    ORDER BY sb1.departure_time
    HAVING COUNT(seat.seat_id) > ? -- 大於購買票數
    """
    params = [train_type, departure, destination, destination, start_time, end_time, counting]
    
    cursor.execute(query, params)
    # trains 資訊包含train_departure_time, train_arrival_time, departure_station, arrival_station, available_seats
    trains = cursor.fetchall()

    connection.close()
    
    # 回傳資料且回報成功
    return {"status": "success", "data": trains}

# 計算車票單價
def calculate_ticket_price(travel_time):
    base_price_per_minute = 2.5  # 基本票價
    concession_discont = 0.5 # 優惠票折扣

    order_list = session.get('order_list', []) # 取得 session['order_list']
    # 根據身分別計算個別票價
    if order_list['ticket_type'] == "regular":
        ticket_price = math.ceil(travel_time * base_price_per_minute)
    elif order_list['ticket_type'] == "concession":
        ticket_price = math.ceil(travel_time * base_price_per_minute * concession_discont)
    
    return ticket_price

# 計算訂單總價
def calculate_total_price_in_session(travel_time):
    total_price = 0
    order_list = session.get('order_list', []) # 取得 session['order_list']
    
    for item in order_list:
        ticket_price = calculate_ticket_price(travel_time)
        total_price += ticket_price

    return total_price

# 加入座位訂購清單
# 建立一個 session 物件當作訂購清單, 儲存使用者選取的座位, 可以全域使用
def add_to_order_list(train_id, car_id, seat_id, ticket_type):
    # 建立訂購清單儲存使用者選取的座位
    if 'order_list' not in session:
        session['order_list'] = []

    order_list = session['order_list']

    # 每一個被選取的座位, 儲存車廂號碼、座位號碼和身分別(用來計算票價)
    selected_seat = {'car_id': car_id, 'seat_id': seat_id, 'ticket_type': ticket_type}
    if selected_seat not in order_list:
        order_list.append(selected_seat)
        session['order_list'] = order_list
    return order_list

# 確認訂購清單內的座位數量和購買車票數量一致
def check_order_consistency(counting):
    order_list = session.get('order_list', []) # 取得 session['order_list']
    if len(order_list) != counting:
        return False
    return True


# 訂購座位(已經確認過訂購清單內的座位數量和購買車票數量一致之後)
# seats 會包含 car_id, seat_id, seat_type
# passenger_info 會包含 user_id, id_no, name, phone, email
def book_seat(train_id, depature, destination, depart_time, arrive_time, passenger_info):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:
        order_list = session.get('order_list', []) # 取得 session['order_list']
        
        for item in order_list:
            # 更新座位狀態
            seat_management.update_seat_be_seated(train_id, item['car_id'], item['seat_id'])

        ### 新增訂單跟票
        # 計算總票價
        travel_time = (arrive_time - depart_time).total_seconds() / 60  # 以分鐘為單位
        total_price = calculate_total_price_in_session(travel_time) 

        # 產生訂單編號, 暫定: 一個"B"加上六位數字的字串, f'B{next_order_num:06d}'
        cursor.execute('SELECT MAX(order_id) FROM orders')
        last_order_id = cursor.fetchone()[0] # 取得當前最後的訂單編號
        next_order_num = (last_order_id or 0) + 1 # 新的訂單編號 = 最後的訂單編號 + 1
        order_id = f'B{next_order_num:06d}'

        # 產生訂票資訊: 訂票時間, 過期時間, 訂單狀態
        booking_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pay_expire_data = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") # 加 1 天
        order_status = "Unpaid"

        '''
        需要在訂單加入訂單總價 total_price
        '''
        cursor.execute('''
                    INSERT INTO order (order_id, train_id, depature, destination, depart_time, arrive_time, user_id, order_status, pay_expire_data, booking_time)
                    VALUES (?, ?, ?, ?)
                    ''', (order_id, train_id, depature, destination, depart_time, arrive_time, passenger_info, order_status, pay_expire_data, booking_timestamp))
            
        for item in order_list:
            # 產生車票編號, 暫定: 一個"T"加上九位數字的字串, f'T{next_ticket_num:09d}'
            cursor.execute('SELECT MAX(ticket_id) FROM tickets')
            last_ticket_id = cursor.fetchone()[0] # 取得當前最後的車票編號
            next_ticket_num = (last_ticket_id or 0) + 1 # 新的車票編號 = 最後的車票編號 + 1
            ticket_id = f'T{next_ticket_num:09d}'
            ticket_price = calculate_ticket_price(travel_time)

            cursor.execute('''
                            INSERT INTO ticket (ticket_id, ticket_type, price, car_id, seat_id, order_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                           ''',(ticket_id, item['ticket_type'], ticket_price, item['car_id'], item['seat_id'], order_id))
        connection.commit()
        return {"status": "success", "message": "Booking successful"}
    
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        connection.close()
