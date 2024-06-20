from flask import Flask, request, jsonify, render_template
from modules.search_train import train_query

app = Flask(__name__)

@app.route('/')
def hello():
    print('sending request to /')
    return 'hello!'

@app.route('/booking', methods=['GET'])
def booking():
    return render_template('booking.html')

@app.route('/search_trains', methods=['GET'])
def search_trains():
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    time1 = request.args.get('time1')
    time2 = request.args.get('time2')
    ticket_number = request.args.get('ticket_number')
    id_number = request.args.get('id_number')

    if not departure or not destination or not date or not time1 or not time2:
        return jsonify({'error': 'Missing parameters'}), 400

    trains = train_query(departure, destination, date)
    if not trains:
        return jsonify({'error': 'No trains found for the given parameters'}), 404
    
    return jsonify(trains)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
