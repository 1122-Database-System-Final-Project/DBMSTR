from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from modules.search_train import train_query
import modules.booking as bk
import modules.seat_management as seat
import modules.order_query as oq
import modules.order_modification as om
import modules.order_deletion as od
import os

app = Flask(__name__)
app.secret_key = "SECRET_6666"

# 設定資料庫路徑
BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIRECTORY, '../database/database.db')

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
        departure = request.form.get('departure')
        destination = request.form.get('destination')
        '''
        用 session 儲存 counting
        '''
        session["counting"] = request.form.get('counting') # 後面會用到, 用 session 儲存
        train_type = request.form.get('train_type') # train_type 有 "自強", "莒光"

        # 檢查是否成功取得資料
        counting = int(session["counting"])
        result = bk.get_all_trains(start_time, end_time, departure, destination, counting, train_type)
        if result["status"] == "error":
            return render_template('query_train.html', trains=[], error_message=result["message"])
        
        # 成功取得資料後, 導航到查詢結果頁面
        trains = result["data"]
        # trains 資訊包含 train.train_id, train.train_type, train_depart_time, train_arrive_time, departure, destination, available_seats
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
    depart_time = request.form.get('train_depart_time').strip()
    arrive_time = request.form.get('train_arrive_time').strip()
    departure = request.form.get('departure')
    destination = request.form.get('destination')
    available_seats = request.form.get('available_seats')
    travel_date = session.get('travel_date').strip()
    counting = session.get('counting')
                            
    cvt_depart_time = datetime.strptime(depart_time, '%H:%M:%S')
    cvt_arrive_time = datetime.strptime(arrive_time, '%H:%M:%S')
    travel_time = (cvt_arrive_time - cvt_depart_time).seconds / 60 # 旅程時間轉換成分鐘數
    print(f"travel_time: {travel_time}")

    # 用一個 session 儲存使用者選擇的車次資料
    session['selected_train'] = {
        'train_id' : train_id,
        'train_type' : train_type,
        'depart_time' : depart_time,
        'arrive_time' : arrive_time,
        'travel_time' : travel_time,
        'departure' : departure,
        'destination' : destination
    }
    
    return render_template('confirm_to_start.html', 
                            train_id=train_id, train_type=train_type,
                            departure_time=depart_time, arrive_time=arrive_time,
                            departure=departure, destination=destination,
                            available_seats=available_seats, travel_date=travel_date, 
                            counting=counting)

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
                    seats_list = [list(s) for s in seats]
                    for s in seats_list:
                        if s[1]== 'window':
                            s[1] = '靠窗'
                        else:
                            s[1] = '靠走道'
                    seats = [tuple(s) for s in seats_list]
                    return render_template('seat_selection.html', train_id=train_id, counting=counting, seats=seats, error_message=error_message)
                else:
                    session['selected_seats'] = selected_seats
                    print(f"selected_seats: {selected_seats}")
                    seat.update_seat_be_seated(selected_seats)
                    return redirect(url_for('confirm_ticket_type'))
            counting = int(request.form['counting'])
            seats = seat.get_all_available_seats_by_train_id(train_id)
            seats_list = [list(s) for s in seats]
            for s in seats_list:
                if s[1]== 'window':
                    s[1] = '靠窗'
                else:
                    s[1] = '靠走道'
            seats = [tuple(s) for s in seats_list]
            return render_template('seat_selection.html', train_id=train_id, counting=counting, seats=seats)
    else:
        train_id = int(session['selected_train']["train_id"])
        counting = int(session["counting"])
        return render_template('seat_selection.html', train_id=train_id, counting=counting)

# 確認票種
@app.route('/confirm_ticket_type', methods=['GET', 'POST'])
def confirm_ticket_type():
    # 獲取選擇座位 selected_seats, 內容是 ['511101', '511102', ...], 若座位為空則得到 []
    selected_seats = session.get('selected_seats', []) 
    # 建立一個 order_list 
    order_list = bk.create_order_list(selected_seats)
    print(f"order_list in '/confirm_ticket_type' before 'POST': {order_list}")

    # 取得使用者提交的資訊
    if request.method == 'POST':
        # travel_time = session['selected_train']['travel_time']
        travel_time = session.get('selected_train', {}).get('travel_time', 0)
        print(f"order_list after 'POST': {order_list}")
        # 更新 order_list 中的 ticket_type 並計算票價
        total_price = 0
        for item in order_list:
            item['ticket_type'] = request.form.get(f'ticket_type_{item["seat_id"]}', '一般')
            item['ticket_price'] = bk.calculate_ticket_price(travel_time, item['ticket_type'])
            total_price += item['ticket_price']

        # 將訂購清單和票價存入session
        session['order_list'] = order_list 
        session['total_price'] = total_price
        print(f"order_list after save to session: {session['order_list']}")
        print(f"total_price after save to session: :{session['total_price']}")

        print("'POST' before render_template('confirm_order.html).")
        return render_template('confirm_order.html', 
                           order_list=order_list, 
                           total_price=total_price)

    # 提供網頁顯示需要的資料
    else:
        print("'GET' before render_template.")
        return render_template('confirm_ticket_type.html',
                               order_list=order_list)


# 確認訂單
@app.route('/confirm_order', methods=['GET', 'POST'])
def confirm_order():

    # 取得使用者提交的資訊
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
        print(f"user after save to session: {session['user']}")

        return redirect(url_for('submit_order'), code=307)  # 使用code=307保持POST方法
    else:
        
        order_list = session.get('order_list', [])
        total_price = session.get('total_price', 0)
        print(f"order_list in 'confirm_order': {order_list}")
        print(f"total_price in 'confirm_order': {total_price}")
        return render_template('confirm_order.html', order_list=order_list, total_price=total_price)

# 提供一個後端API端點, 當使用者在confirm_order.html中選擇車票類型時會觸發function updateTotalPrice()
# 這個函式使用fetch API發送POST請求到/calculate_ticket_price
@app.route('/calculate_ticket_price_api', methods=['POST'])
def calculate_ticket_price_api():
    data = request.json
    seat_id = data.get('seat_id')
    ticket_type = data.get('ticket_type')

    travel_time = session.get('selected_train', {}).get('travel_time', 0)
    price = bk.calculate_ticket_price(travel_time, ticket_type)

    return jsonify({'price': price})

# 送出訂單
@app.route('/submit_order', methods=['POST', 'GET'])
def submit_order():
    if request.method == 'POST':
        # 獲取訂購清單和票價信息
        selected_train = session.get('selected_train', {})
        order_list = session.get('order_list', [])
        total_price = session.get('total_price', 0)
        user = session.get('user', {})

        print(f"selected_train: {selected_train}")
        print(f"order_list: {order_list}")
        print(f"selectetotal_priced_train: {total_price}")
        print(f"user: {user}")

        # 產生訂單和車票編號，並更新資料庫
        result = bk.book_seat(selected_train, order_list, total_price, user)
        print(f"result: {result}")
        if result["status"] == "error":
            return render_template('submit_order.html', booking_result=[], error_message=result["message"])
        
        booking_result = result["data"]
        return render_template('submit_order.html', booking_result=booking_result)
    else:
        # 處理直接訪問/submit_order頁面的情況
        return redirect(url_for('confirm_order'))

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
        #print(order_details["seats"])
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
            return render_template('order_modification.html', message=error_message)
        
        # 查詢訂單
        order_details = oq.query_order(id_no, order_id)  # 使用從 order_query.py 引用的函數
        if not order_details:
            error_message = "Order not found"
            return render_template('order_modification.html', message=error_message,id_no=id_no,order_id=order_id)
        
        #刪除原本座位狀態
        original_seats=om.find_original_seat(order_id)
        seat.delete_seated_seat(original_seats) 

        counting = order_details["total_tickets"]
        # 找新座位
        if 'seats' in request.form:
            selected_seats = request.form.getlist('seats')
            print(selected_seats)
            if len(selected_seats) != counting:
                error_message = f"請再選一次！您應該要選{counting}個座位。"
                empty_seats = seat.get_all_available_seats_by_train_id(order_details["train_id"])
                return render_template('seat_selection_for_modify.html',order_details=order_details, train_id=order_details["train_id"], counting=counting, seats=empty_seats, error_message=error_message,id_no=id_no)                
            else:
                #selected_seats = [int(seat) for seat in selected_seats]
                print(selected_seats)
                return render_template('confirm_modification.html',order_details=order_details, train_id=order_details["train_id"], seats=selected_seats,order_id=order_id,id_no=id_no)            

        empty_seats = seat.get_all_available_seats_by_train_id(order_details["train_id"])
        return render_template('seat_selection_for_modify.html',order_details=order_details, train_id=order_details["train_id"], counting=counting, seats=empty_seats,id_no=id_no)
        
    elif request.method == 'GET':
        id_no = request.args.get('id_no')
        order_id = request.args.get('order_id')
        if not id_no or not order_id:
            error_message = "Both ID number and Order ID are required."
            return render_template('confirm_modification.html', message=error_message)
        
        # 查詢訂單
        order_details = oq.query_order(id_no, order_id)
        if not order_details:
            error_message = "Order not found"
            return render_template('confirm_modification.html', order_details=order_details,message=error_message, id_no=id_no, order_id=order_id)
        
        seats = seat.get_all_available_seats_by_train_id(order_details["train_id"])
        return render_template('seat_selection_for_modify.html',order_details=order_details, train_id=order_details["train_id"], counting=order_details["total_tickets"], seats=seats)
    

@app.route('/confirm_modification', methods=['GET','POST'])
def confirm_modification():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        selected_seats = request.form.get('selected_seats')
        if isinstance(selected_seats, str):
            selected_seats = [int(seat.strip().replace("'", "")) for seat in selected_seats.strip('[]').split(',')]
        print("select: ",selected_seats)
        seat.update_seat_be_seated(selected_seats)
        om.change_my_seat(order_id,selected_seats)
        success_message = "訂單修改成功！"
        return render_template('modification_success.html', success_message=success_message)
    
    # 如果是GET請求，顯示確認修改頁面
    train_id = request.args.get('train_id')
    seats = request.args.get('new_seats').split(',')
    order_id = request.args.get('order_id')
    
    order_details = {
        "order_id":order_id,
        "train_id": train_id,
        "new_seats": seats,
    }
    
    return render_template('confirm_modification.html', order_details=order_details)
    


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

        return render_template('order_deletion.html',order_id=order_id,id_no=id_no)
    else:
        return render_template('order_deletion.html', order_id=order_id,id_no=id_no)


@app.route('/confirm_delete_order', methods=['POST'])
def confirm_delete_order():
    if request.method=='POST':
        order_id = request.form.get('order_id')
        id_no = request.form.get('id_no')
    
        if not id_no or not order_id:
            error_message = "Both ID number and Order ID are required."
            return render_template('order_deletion.html', error_message=error_message, order_id=order_id, id_no=id_no)
    
        # 刪除訂單
        od.delete_order(order_id)
    
        success_message = "訂單成功取消"
        return render_template('confirm_deletion.html', success_message=success_message)
    else:
        return render_template('order_deletion.html',order_id=order_id,id_no=id_no)

#查詢列車
@app.route('/search_train', methods=['GET','POST'])
def search_train():
    if request.method == 'POST':
        departure = request.form.get('departure')
        destination = request.form.get('destination')
        departure_time_1 = request.form.get('departure_time1')
        departure_time_2 = request.form.get('departure_time2') 

        if not departure or not destination or not departure_time_1 or not departure_time_2:
            return jsonify({'error': 'Missing parameters'}), 400

        trains = train_query(departure, destination, departure_time_1, departure_time_2)
        if not trains:
            return jsonify({'error': 'No trains found for the given parameters'}), 404
        
        return render_template('search_train_result.html', trains=trains)
    else:
        return render_template('search_train.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
