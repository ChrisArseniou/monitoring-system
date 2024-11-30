from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import datetime
import random
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['JWT_SECRET'] = 'jwt-secret-key'
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

# JWT Helper Functions
def generate_token(user_id):
    """Generate a JWT token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')

def verify_token(token):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Decorator to protect routes
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token is None or not token.startswith('Bearer '):
            return jsonify({"error": "Token is missing or invalid"}), 401
        user_id = verify_token(token.split(' ')[1])
        if user_id is None:
            return jsonify({"error": "Token is invalid or expired"}), 401
        return f(*args, **kwargs)
    return decorated_function

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
@jwt_required
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
@jwt_required
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

# User login endpoint for JWT generation
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Example hardcoded user (replace with database check in production)
    if username == 'admin' and password == 'password':
        token = generate_token(user_id=1)
        return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid username or password'}), 401

# Simulate data from 50 microcontrollers
@app.route('/simulate', methods=['POST'])
@jwt_required
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
