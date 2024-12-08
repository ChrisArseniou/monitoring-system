IoT Relay Monitoring and Environmental Data Logger

This project monitors relay states and environmental data (temperature and humidity) using an Arduino-compatible microcontroller with Ethernet. It sends the data to a Flask API server.
Features

    Ethernet connection for reliable network communication.
    Reads relay states (on/off).
    Reads temperature and humidity using a DHT sensor.
    Sends data as JSON to a Flask API.
    Periodic data reading using a timer.

Hardware Needed

    Microcontroller (e.g., ESP32 with Ethernet support)
    LAN8720 Ethernet module
    DHT11 or DHT22 sensor
    Up to 5 relays
    Ethernet cable
    Power supply

Software Needed

    Arduino IDE
    DHT Sensor Library
    ArduinoJson Library
    Flask (Python web server)

Circuit Setup

    Connect the LAN8720 module for Ethernet.
    Connect the DHT sensor to GPIO4.
    Connect up to 5 relays to IO39, IO36, IO15, IO14, and IO12.
