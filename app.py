from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from modules.search_train import train_query
import modules.booking as bk
import modules.seat_management as seat
import modules.order_query as oq
import modules.order_modification as om
import modules.order_deletion as od

app = Flask(__name__)
app.secret_key = "SECRET_6666"

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 開始訂票
@app.route('/query_train', methods=['GET', 'POST'])
def query_train():
    # 取得使用者提交的資訊
    if request.method == 'POST': 
        # request.form 是 Flask 提供的物件, 用來存取 POST 請求提交的資訊,
        # request.form 是一個字典, 它會從 query_train.html 提交的表單數據中獲取 name 屬性為 select_items 的表單元素的值
        '''
        用 session 儲存 travel_date
        '''
        session["travel_date"] = request.form.get('travel_date') 
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        departure = '%' + request.form.get('departure') + '%'
        destination = '%' + request.form.get('destination') + '%'
        '''
        用 session 儲存 counting
        '''
        session["counting"] = request.form.get('counting') # 後面會用到, 用 session 儲存
        train_type = '%' + request.form.get('train_type') + '%' # train_type 有 "自強", "莒光"

        # 檢查是否成功取得資料
        counting = int(session["counting"])
        result = bk.get_all_trains(start_time, end_time, departure, destination, counting, train_type)
        if result["status"] == "error":
            return render_template('query_train.html', trains=[], error_message=result["message"])
        
        # 成功取得資料後, 導航到查詢結果頁面
        trains = result["data"]
        # trains 資訊包含 train.train_id, train.train_type, train_departure_time, train_arrival_time, departure_station, arrival_station, available_seats
        # 例如 [(511, ' 08:43:00', ' 10:43:00', ' 七堵', ' 新竹', 80)]
        
        return render_template('query_train_results.html', trains=trains)
    
    # 提供網頁顯示需要的資料
    else:
        # 檢查是否成功取得資料
        result = bk.get_all_stations_names()
        if result["status"] == "error":
            return render_template('query_train.html', stations=[], error_message=result["message"])
        
        # 成功取得資料後, 回傳火車時刻表
        stations_name_list = result["data"]
        return render_template('query_train.html', stations=stations_name_list)

# 訂票結果決定車次
@app.route('/confirm_to_start', methods=['POST'])
def confirm_to_start():
    # 取得使用者提交的資訊

    train_id = request.form.get('train_id')
    train_type = request.form.get('train_type')
    depart_time = request.form.get('departure_time').strip()
    arrival_time = request.form.get('arrival_time').strip()
    departure_station = request.form.get('departure_station')
    arrival_station = request.form.get('arrival_station')
    available_seats = request.form.get('available_seats')
    travel_date = session.get('travel_date')
    counting = session.get('counting')
                            
    cvt_depart_time = datetime.strptime(depart_time, '%H:%M:%S')
    cvt_arrival_time = datetime.strptime(arrival_time, '%H:%M:%S')
    travel_time = (cvt_arrival_time - cvt_depart_time).seconds / 60 # 旅程時間轉換成分鐘數

    # 用一個 session 儲存使用者選擇的車次資料
    session['selected_train'] = {
        'train_id' : train_id,
        'train_type' : train_type,
        'depart_time' : depart_time,
        'arrival_time' : arrival_time,
        'travel_time' : travel_time,
        'departure' : departure_station,
        'destination' : arrival_station
    }
    
    return render_template('confirm_to_start.html', train_id=train_id, train_type=train_type,
                        departure_time=depart_time, arrival_time=arrival_time,
                        departure_station=departure_station, arrival_station=arrival_station,
                        available_seats=available_seats, travel_date=travel_date, counting=counting)

# 選座位
@app.route('/select_seats', methods=['GET', 'POST'])
def select_seats():
    if request.method == 'POST':
        train_id = int(request.form.get('train_id'))
        if 'counting' in request.form:
            if 'seats' in request.form:
                counting = int(request.form['counting'])
                selected_seats = request.form.getlist('seats')
                if len(selected_seats) != counting:
                    error_message = f"請再選一次！您應該要選{counting}個座位。"
                    seats = seat.get_all_available_seats_by_train_id(train_id)
                    return render_template('seat_selection.html', train_id=train_id, counting=counting, seats=seats, error_message=error_message)
                else:
                    print(selected_seats)
                    return redirect(url_for('confirm_order', train_id=train_id, seats=','.join(selected_seats)))
            counting = int(request.form['counting'])
            seats = seat.get_all_available_seats_by_train_id(train_id)
            return render_template('seat_selection.html', train_id=train_id, counting=counting, seats=seats)
    else:
        train_id = int(session['selected_train']["train_id"])
        counting = int(session["counting"])
        return render_template('seat_selection.html', train_id=train_id, counting=counting)


# 確認訂單
@app.route('/confirm_order', methods=['GET'])
def confirm_order():
    '''
    order_list 需要再根據前面的部分調整
    '''
    order_list = request.form.getlist('order_list') # 獲取訂購清單
    travel_time = session['selected_train']['travel_time']

    # 計算票價和總價
    total_price = 0
    for item in order_list:
        price = bk.calculate_ticket_price(travel_time, item['ticket_type'])
        total_price += price
        item['ticket_price'] = price

    # 將訂購清單和票價存入session
    session['order_list'] = order_list 
    session['total_price'] = total_price
    print(f"order_list:{order_list}")
    print(f"total_price:{total_price}")

    return render_template('confirm_order.html', order_list=order_list, total_price=total_price)

# 送出訂單
@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        # 獲取聯絡資訊
        name = request.form['name']
        id_no = request.form['id_no']
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 檢查聯絡資訊的格式正確性
        if not name or not id_no:
            return "聯絡資訊錯誤，請重新填寫", 400
        # 儲存使用者資料
        session['user'] = {
            'name' : name,
            'id_no' : id_no,
            'phone' : phone,
            'email' : email
        }
        # 獲取訂購清單和票價信息
        selected_train = session['selected_train']
        order_list = session['order_list']
        total_price = session['total_price']
        user = session['user']
  
        # 產生訂單和車票編號，並更新資料庫
        result = bk.book_seat(selected_train, order_list, total_price, user)
        booking_result = result['data']
        return render_template('submit_order.html', booking_result=booking_result)


#查詢訂單
@app.route('/query_order', methods=['GET', 'POST'])
def look_at_my_order():
    if request.method == 'POST':
        id_no = request.form.get('id_no')
        order_id = request.form.get('order_id')

        if not (id_no and order_id):
            error_message = "Both ID number and Order ID are required."
            return render_template('order_query.html', order_details=None, error_message=error_message)

        order_details = oq.query_order(id_no, order_id)

        if order_details:
            return render_template('order_query.html', order_details=order_details, error_message=None,id_no=id_no)
        else:
            error_message = "Order not found."
            return render_template('order_query.html', order_details=None, error_message=error_message)
    else:
        return render_template('order_query.html', order_details=None)
    

#修改訂單 查詢->查看空座位->修改座位
@app.route('/modify_order', methods=['GET','POST'])
def modify_order():
    if request.method == 'POST':
        id_no = request.form.get('id_no')
        order_id = request.form.get('order_id')
        if not id_no or not order_id:
            error_message = "Both ID number and Order ID are required."
            return render_template('order_query.html', message=error_message)
    
        # 查詢訂單
        order_details = oq.query_order(id_no, order_id)  # 使用從 order_query.py 引用的函數
        if not order_details:
            error_message = "Order not found"
            return render_template('order_query.html', message=error_message)
    
        # 找新座位
        empty_seats = seat.get_all_available_seats_by_train_id(order_details["train_id"])

        new_seats = request.form.getlist('new_seats')
        if not new_seats:
            error_message = "No seats selected"
            return render_template('order_modification.html', message=error_message)

        # 更新座位
        om.change_my_seat(order_id, order_details["train_id"], new_seats)

        success_message = "Order updated successfully"
        return render_template('order_modification.html', message=success_message)
    else:
        return render_template('order_modification.html', message=None)



#刪除訂單
@app.route('/delete_order', methods=['POST'])
def delete_order():
    if request.method == 'POST':
        id_no = request.form.get('id_no')
        order_id = request.form.get('order_id')
        if not id_no or not order_id:
            error_message = "Both ID number and Order ID are required."
            return render_template('order_deletion.html', message=error_message,order_id=order_id,id_no=id_no)
    
        # 查詢訂單
        order_details = oq.query_order(id_no, order_id)  # 使用從 order_query.py 引用的函數

        if not order_details:
            error_message = "Order not found"
            return render_template('order_deletion.html', message=error_message,order_id=order_id,id_no=id_no)
    
        od.delete_order(order_id,order_details["train_id"])

        success_message = "訂單成功取消"
        return render_template('order_deletion.html', message=success_message,order_id=order_id,id_no=id_no)
    else:
        return render_template('order_deletion.html', message=None)

#查詢列車
@app.route('/search_trains', methods=['GET'])
def search_trains():
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')

    if not departure or not destination or not date:
        return jsonify({'error': 'Missing parameters'}), 400

    trains = train_query(departure, destination, date)
    if not trains:
        return jsonify({'error': 'No trains found for the given parameters'}), 404
    
    return jsonify(trains)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
