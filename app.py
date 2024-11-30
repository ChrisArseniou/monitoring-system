from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import datetime
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# SQLite Database setup
def init_db():
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sensor_id INTEGER NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL
                )''')
    conn.commit()
    conn.close()

# Insert event into the database
def log_event(sensor_id, temperature, humidity):
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute("INSERT INTO events (timestamp, sensor_id, temperature, humidity) VALUES (?, ?, ?, ?)",
              (datetime.datetime.now().isoformat(), sensor_id, temperature, humidity))
    conn.commit()
    conn.close()

# Simulate receiving data from microcontrollers (mocking serial communication)
@app.route('/send_data', methods=['POST'])
def receive_data():
    data = request.json
    sensor_id = data.get('sensor_id')
    temperature = data.get('temperature')
    humidity = data.get('humidity')

    if not all([sensor_id, temperature, humidity]):
        return jsonify({"error": "Invalid data"}), 400

    log_event(sensor_id, temperature, humidity)

    # Trigger alarms if critical values are detected
    if temperature > 40 or humidity < 20:
        socketio.emit('alarm', {'sensor_id': sensor_id, 'temperature': temperature, 'humidity': humidity})

    return jsonify({"message": "Data logged successfully"}), 200

# Get recent events
@app.route('/events', methods=['GET'])
def get_events():
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()

    events = [
        {
            "id": row[0],
            "timestamp": row[1],
            "sensor_id": row[2],
            "temperature": row[3],
            "humidity": row[4]
        } for row in rows
    ]

    return jsonify(events)

# Real-time WebSocket events
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('message', {'message': 'Connected to the monitoring system'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Simulate data from 50 microcontrollers
@app.route('/simulate', methods=['POST'])
def simulate_data():
    for sensor_id in range(1, 51):
        temperature = random.uniform(15.0, 50.0)
        humidity = random.uniform(10.0, 90.0)
        log_event(sensor_id, temperature, humidity)

        if temperature > 40 or humidity < 20:
            socketio.emit('alarm', {'sensor_id': sensor_id, 'temperature': temperature, 'humidity': humidity})

    return jsonify({"message": "Simulation completed"}), 200

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
