from flask import Flask, render_template, request, redirect, url_for
import modules.booking as bk

app = Flask(__name__)


@app.route('/query_train_no', methods=['GET', 'POST'])
def query_train_no():
    # 取得使用者提交的資訊
    if request.method == 'POST': 
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        counting = request.form.get('counting')
        ticket_type = request.form.get('ticket_type')
        
        # 檢查所有字段是否已填寫
        if not (start_time and end_time and start_station and end_station and counting and ticket_type):
            error_message = "All fields are required."
            return render_template('train_schedule.html', trains=[], error_message=error_message)

        # 檢查是否成功取得資料
        result = bk.get_all_trains(start_time, end_time, start_station, end_station, counting, ticket_type)
        if result["status"] == "error":
            return render_template('train_schedule.html', trains=[], error_message=result["message"])
        
        # 成功取得資料後, 回傳火車時刻表
        trains = result["data"]
        return render_template('train_schedule.html', trains=trains)
    else:
        return render_template('train_schedule.html', trains=[])

# 選座位
@app.route('/select_seats/<train_id>', methods=['GET', 'POST'])
def select_seats(train_id):
    if request.method == 'POST':
        counting = request.form.get('counting')
        seats = request.form.getlist('seats')
        if len(seats) != int(counting):
            error_message = f"You must select exactly {counting} seats."
            return render_template('seat_selection.html', train_id=train_id, error_message=error_message)
        
        return redirect(url_for('booking_inquiry', train_id=train_id, seats=','.join(seats)))
    else:
        seats = bk.get_all_seats_by_train_id(train_id)
        return render_template('seat_selection.html', seats=seats, train_id=train_id)

@app.route('/booking_inquiry', methods=['GET', 'POST'])
def booking_inquiry():
    if request.method == 'POST':
        train_id = request.form['train_id']
        seats = request

if __name__ == '__main__':
    app.run(debug=True)
