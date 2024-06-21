import sqlite3
from flask import session
import os
import math
from datetime import datetime, timedelta
from . import seat_management as sm

'''
路徑可能需要根據作業系統調整
'''
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) # 取得當前檔案所在目錄的絕對路徑
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db') # 導航到目錄位置


# 獲取所有車站名稱以供選擇
def get_all_stations_names():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""
                   SELECT TRIM(station_name) 
                   FROM station
                   """)
    stations = cursor.fetchall()
    print(f"stations: {stations}")
    connection.close()
    return {"status": "success", "data": [station[0] for station in stations]}

# 獲取所有班次以供選擇
def get_all_trains(start_time, end_time, departure, destination, counting, train_type):
    
    # 如果資料不完整則不能查詢
    if not (start_time and end_time and departure and destination and counting and train_type):
        return {"status": "error", "message": "All fields are required"}

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = """
    SELECT
        train.train_id, -- 車次
        train.train_type, -- 火車類型 
        sb1.departure_time AS train_depart_time, -- 出發時間
        sb2.arrival_time AS train_arrival_time, -- 抵達時間
        st1.station_name AS departure_station, -- 出發車站
        st2.station_name AS arrival_station, -- 抵達車站
        COUNT(seat.seat_id) AS available_seats -- 剩餘座位數
    FROM train
    JOIN stopped_by sb1 ON train.train_id = sb1.train_id
    JOIN stopped_by sb2 ON train.train_id = sb2.train_id
    JOIN station st1 ON sb1.station_id = st1.station_id
    JOIN station st2 ON sb2.station_id = st2.station_id
    JOIN car ON train.train_id = car.train_id
    JOIN seat ON car.car_id = seat.car_id
    WHERE train.train_type LIKE ? -- 火車類型
        AND st1.station_name LIKE ? -- 出發車站
        AND st2.station_name LIKE ? -- 目標車站
        -- AND sb1.departure_time >= ? -- 開始時間
        -- AND sb1.departure_time <= ? -- 結束時間
        AND sb1.arrival_time < sb2.departure_time
        AND seat.occupied LIKE '%n%' -- 車位沒有被佔用
    GROUP BY train.train_id, sb1.departure_time, sb2.arrival_time, st1.station_name, st2.station_name
    HAVING COUNT(seat.seat_id) >= ? -- 大於購買票數
    ORDER BY sb1.departure_time
    """
    params = [train_type, departure, destination, counting]
    print(f"params: {params}")

    cursor.execute(query, params)
    # trains 資訊包含 train.train_id, train.train_type, train_depart_time, train_arrival_time, departure_station, arrival_station, available_seats
    trains = cursor.fetchall()
    print(f"trains: {trains}")

    connection.close()
    
    # 回傳資料且回報成功
    return {"status": "success", "data": trains}

# 計算車票單價
def calculate_ticket_price(travel_time, ticket_type):
    base_price_per_minute = 2.5  # 基本票價
    concession_discont = 0.5 # 優惠票折扣

    # 根據身分別計算個別票價
    if ticket_type == "一般":
        ticket_price = math.ceil(travel_time * base_price_per_minute)
    elif ticket_type == "優待":
        ticket_price = math.ceil(travel_time * base_price_per_minute * concession_discont)
    
    return ticket_price

# # 計算訂單總價
# def calculate_total_price(ticket_prices):
#     total_price = 0
    
#     for price in ticket_prices:
#         total_price += price

#     return total_price

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
'''
session['selected_train'] = {
    'train_id' : train[0],
    'depart_time' : train[1],
    'arrival_time' : train[2],
    'travel_time' : travel_time,
    'departure' : train[3],
    'destination' : train[4]
}
order_list = [
{
    'car_id': ####, 
    'seat_id': ######,
    'ticket_type': '一般',
    'ticket_price': ###
},
{
    'seat_id': ######,,
    'ticket_type': '優待'
},...
]
ticket_prices = [###, ###, ...]
ticket_prices = ###
session['user'] = {
    'name' : name,
    'id_no' : id_no,
    'phone' : phone,
    'email' : email
}
'''
def book_seat(selected_train, order_list, total_price, user):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:
        train_id = selected_train['train_id']

        ### 新增使用者, 訂單, 票
        # 產生使用者編號
        cursor.execute('''
                       SELECT MAX(user_id) 
                       FROM user
                       ''')
        last_user_id = cursor.fetchone()[0] # 取得當前最後的使用者編號
        next_user_id = (last_user_id or 0) + 1 # 新的使用者編號 = 最後的使用者編號 + 1

        # 新增使用者資料
        cursor.execute('''
                       INSERT INTO user (user_id, name, id_no, phone, email)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (next_user_id, user['name'], user['id_no'], user['phone'], user['email']))

        # 產生訂單編號
        cursor.execute('''
                       SELECT MAX(order_id) 
                       FROM [order]
                       ''')
        last_order_id = cursor.fetchone()[0] # 取得當前最後的訂單編號
        next_order_id = (last_order_id or 0) + 1 # 新的訂單編號 = 最後的訂單編號 + 1

        # 產生訂單資訊
        departure = selected_train['departure']
        destination = selected_train['destination']
        depart_time = selected_train['depart_time']
        arrive_time = selected_train['arrive_time']
        booking_timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        
        travel_date = datetime.strptime(session["travel_date"], '%y-%m-%d')
        pay_expire_date = (travel_date - timedelta(days=1)).strftime("%y-%m-%d") # 旅遊日期減 1 天
        
        order_status = "未付款"

        '''
        需要在訂單加入訂單總價 total_price
        '''
        cursor.execute('''
                    INSERT INTO order (order_id, train_id, departure, destination, depart_time, arrive_time, user_id, order_status, pay_expire_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (next_order_id, train_id, departure, destination, depart_time, arrive_time, next_user_id, order_status, pay_expire_date, booking_timestamp))
        
        for item in order_list:
            # 更新座位狀態
            sm.update_seat_be_seated(train_id, item['car_id'], item['seat_id'])

            # 產生車票編號, 暫定: 一個"T"加上九位數字的字串, f'T{next_ticket_num:09d}'
            cursor.execute('''
                           SELECT MAX(ticket_id) 
                           FROM ticket
                           ''')
            last_ticket_id = cursor.fetchone()[0] # 取得當前最後的車票編號
            next_icket_id = (last_ticket_id or 0) + 1 # 新的車票編號 = 最後的車票編號 + 1

            cursor.execute('''
                            INSERT INTO ticket (ticket_id, ticket_type, price, car_id, seat_id, order_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                           ''',(next_icket_id, item['ticket_type'], item['ticket_price'], item['car_id'], item['seat_id'], next_order_id))
        connection.commit()
        
        booking_result = {
            'order_id': next_order_id,
            'order_list': order_list,
            'total_price': total_price,
            'pay_expire_date': pay_expire_date
        }
        print(f"trains: {booking_result}")

        return {"status": "success", "data": booking_result}
    
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        connection.close()
