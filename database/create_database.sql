CREATE TABLE IF NOT EXISTS [order](
    order_id INTEGER PRIMARY KEY, 
    train_id INTEGER NOT NULL, departure TEXT NOT NULL, 
    destination TEXT NOT NULL, depart_time TEXT NOT NULL, 
    arrive_time TEXT NOT NULL, user_id INTEGER NOT NULL, 
    order_status TEXT, pay_expire_date TEXT, timestamp TEXT,
    FOREIGN KEY(train_id) REFERENCES train(train_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id));
CREATE TABLE IF NOT EXISTS user(
    user_id INTEGER PRIMARY KEY, 
    id_no TEXT NOT NULL, name TEXT NOT NULL, 
    phone TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS train(
    train_id INTEGER PRIMARY KEY, train_type TEXT);
CREATE TABLE IF NOT EXISTS ticket(
    ticket_id INTEGER PRIMARY KEY, 
    ticket_type TEXT NOT NULL, price INTEGER NOT NULL,
    car_id INTEGER NOT NULL, seat_id INTEGER NOT NULL, 
    order_id INTEGER NOT NULL,
    FOREIGN KEY(seat_id) REFERENCES seat(seat_id),
    FOREIGN KEY(order_id) REFERENCES [order](order_id));
CREATE TABLE IF NOT EXISTS car(
    car_id INTEGER PRIMARY KEY, 
    seat_amount INTEGER NOT NULL, train_id INTEGER NOT NULL,
    FOREIGN KEY(train_id) REFERENCES train(train_id));
CREATE TABLE IF NOT EXISTS seat(
    seat_id INTEGER PRIMARY KEY, 
    car_id INTEGER NOT NULL, occupied TEXT NOT NULL, seat_type TEXT, 
    FOREIGN KEY(car_id) REFERENCES car(car_id));
CREATE TABLE IF NOT EXISTS station(
    station_id INTEGER PRIMARY KEY, station_name TEXT  NOT NULL);
CREATE TABLE IF NOT EXISTS stopped_by(
    train_id INTEGER NOT NULL, station_id INTEGER NOT NULL, 
    arrival_time TEXT NOT NULL, departure_time TEXT NOT NULL,
    FOREIGN KEY(train_id) REFERENCES train(train_id),
    FOREIGN KEY(station_id) REFERENCES station(station_id));
CREATE TABLE IF NOT EXISTS service(
    car_id INTEGER NOT NULL, service_type TEXT NOT NULL,
    FOREIGN KEY(car_id) REFERENCES car(car_id));
