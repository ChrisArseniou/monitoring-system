# IoT Relay Monitoring and Environmental Data Logger

This project demonstrates an IoT-based solution for monitoring relay states and environmental conditions using an Arduino-compatible microcontroller with Ethernet connectivity. The system reads relay states and environmental data (temperature and humidity) from sensors, formats the data as JSON, and sends it to a Flask-based API server for further processing.

## Features

- **Ethernet Connectivity:** Uses the LAN8720 Ethernet PHY module for reliable network communication.
- **Relay Monitoring:** Reads the state of multiple relays (on/off) connected to the microcontroller.
- **Environmental Data Logging:** Monitors temperature and humidity using a DHT sensor (DHT11 or DHT22).
- **JSON Data Transmission:** Sends data as JSON payloads to a Flask API endpoint.
- **Soft Timer:** Manages periodic tasks such as reading sensor values and sending data.

## Hardware Requirements

- Microcontroller (e.g., ESP32 with Ethernet module support)
- LAN8720 Ethernet PHY module
- DHT11/DHT22 temperature and humidity sensor
- Relays (up to 5, for this implementation)
- Ethernet cable
- Power supply

## Software Requirements

- Arduino IDE
- DHT Sensor Library ([available via Arduino Library Manager](https://github.com/adafruit/DHT-sensor-library))
- ArduinoJson Library ([available via Arduino Library Manager](https://arduinojson.org/))
- Flask (Python-based web server)

## Circuit Configuration

1. **Ethernet Connection:**
   - Connect the LAN8720 Ethernet module to the microcontroller. Use the defined pins for MDC, MDIO, and clock input (GPIO0).

2. **DHT Sensor:**
   - Connect the DHT sensor to the specified pin (default: GPIO4).

3. **Relay Inputs:**
   - Connect up to 5 relays to the microcontroller pins (IO39, IO36, IO15, IO14, IO12).


## How It Works

1. The system initializes the Ethernet module and connects to the network.
2. It reads the state of the relays periodically (every 60 seconds).
3. It also reads temperature and humidity from the DHT sensor.
4. The data is structured in JSON format, including:
   - `sensor_id`: Unique ID for the sensor (relay or environmental data).
   - `state`: Relay state (0 or 1) for relay sensors.
   - `temperature`: Temperature value from the DHT sensor.
   - `humidity`: Humidity value from the DHT sensor.
   - `timestamp`: The time of data collection in milliseconds since startup.
5. The JSON data is sent to the Flask API via HTTP POST.

## Example JSON Payloads

### Relay State
```json
{
  "sensor_id": 1,
  "state": 1,
  "timestamp": "123456"
}

    Connect up to 5 relays to IO39, IO36, IO15, IO14, and IO12.
