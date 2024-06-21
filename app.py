from flask import Flask, session, render_template, request, redirect, url_for, jsonify
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
        # request.form 是一個字典, 它會從在 /get_all_trains_id 提交的表單數據中獲取 name 屬性為 select_items 的表單元素的值
        session["booking_date"] = request.form.get('booking_date') # 建立訂單才會用到, 用 session 儲存
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        departure = '%' + request.form.get('departure') + '%'
        destination = '%' + request.form.get('destination') + '%'
        session["counting"] = request.form.get('counting') # 後面會用到, 用 session 儲存
        train_type = '%' + request.form.get('train_type') + '%' # train_type 有 "自強", "莒光"

               
        # 檢查是否成功取得資料
        counting = int(session["counting"])
        result = bk.get_all_trains(start_time, end_time, departure, destination, counting, train_type)
        if result["status"] == "error":
            return render_template('query_train.html', trains=[], error_message=result["message"])
        
        # 成功取得資料後, 導航到查詢結果頁面
        trains = result["data"]
        # trains 資訊包含 train_departure_time, train_arrival_time, departure_station, arrival_station, available_seats
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


# 選座位
@app.route('/select_seats/<train_id>', methods=['GET', 'POST'])
def select_seats(train_id):
    if request.method == 'POST':
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
        return render_template('seat_selection.html', train_id=train_id)


@app.route('/confirm_order', methods=['GET', 'POST'])
def confirm_order():
    return render_template('confirm_order.html')


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
