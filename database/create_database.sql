CREATE TABLE IF NOT EXISTS [order](
    order_id INTEGER PRIMARY KEY, train_id INTEGER, departure TEXT, destination TEXT, depart_time TEXT, arrive_time TEXT, user_id INTEGER, order_status TEXT, pay_expire_date TEXT, timestamp TEXT);
CREATE TABLE IF NOT EXISTS user(
    user_id INTEGER PRIMARY KEY, id_no TEXT, name TEXT, phone TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS train(
    train_id INTEGER PRIMARY KEY, train_type TEXT);
CREATE TABLE IF NOT EXISTS ticket(
    ticket_id INTEGER PRIMARY KEY, ticket_type TEXT, price INTEGER, seat_id INTEGER, order_id INTEGER);
CREATE TABLE IF NOT EXISTS car(
    car_id INTEGER PRIMARY KEY, seat_amount INTEGER, train_id INTEGER);
CREATE TABLE IF NOT EXISTS seat(
    seat_id INTEGER PRIMARY KEY, occupied TEXT, seat_type TEXT, car_id INTEGER);
CREATE TABLE IF NOT EXISTS station(
    station_id INTEGER PRIMARY KEY, station_name TEXT);
CREATE TABLE IF NOT EXISTS stopped_by(
    train_id INTEGER, station_id INTEGER, arrival_time TEXT, departure_time TEXT);
CREATE TABLE IF NOT EXISTS service(
    car_id INTEGER, service_type TEXT);
