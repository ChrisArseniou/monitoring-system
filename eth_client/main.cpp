#include <Arduino.h>
#include <ETH.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <SPI.h>
#include <SoftTimer.h>
#include <ArduinoJson.h>
#include <DHT.h>  // Include the DHT sensor library

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// Ethernet and sensor configuration (same as before)
#define ETH_PHY_TYPE        ETH_PHY_LAN8720
#define ETH_PHY_MDC         23
#define ETH_PHY_MDIO        18
#define ETH_CLK_MODE        ETH_CLOCK_GPIO0_IN

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 1, 8);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

HTTPClient http;
String host = "http://<flask-ip>:<port>/send_data";  // Flask endpoint to receive sensor data

// Pin assignments and DHT sensor setup
#define DHT_PIN 4      // Define the pin where the DHT sensor is connected
#define DHT_TYPE DHT22  // Specify the DHT sensor model (DHT11 or DHT22)
DHT dht(DHT_PIN, DHT_TYPE);  // Initialize DHT sensor

void readState(int pin, int sensorid);

// Function to initialize the Ethernet connection (same as before)
void ETH_init()
{
  Serial.println("Connecting to ethernet...");
  ETH.begin(ETH_PHY_ADDR, ETH_PHY_POWER, ETH_PHY_MDC, ETH_PHY_MDIO, ETH_PHY_TYPE, ETH_CLK_MODE);
  ETH.macAddress(mac);
  ETH.config(ip, gateway , subnet);
}

// Task to read the state of the relays and temperature/humidity every 60 seconds
Task readRelays(60000, [](Task *me)
                { 
                  // readState(IO39, 1);
                  // readState(IO36, 2);
                  // readState(IO15, 3);
                  // readState(IO14, 4);
                  // readState(IO12, 5);
                  readTemperatureHumidity();  // Read and send temperature and humidity
                });

void setup()
{
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector for module
  Serial.begin(115200);
  while (!Serial && millis() < 5000)
    ;
  ETH_init();

  // Wait for Ethernet connection
  while (!ETH.linkUp())
  {
    delay(100);
    Serial.println("Waiting for Ethernet connection...");
  }
  Serial.print("Connected! IP address: ");
  Serial.println(ETH.localIP());

  pinMode(IO39, INPUT_PULLUP);
  pinMode(IO36, INPUT_PULLUP);
  pinMode(IO15, INPUT_PULLDOWN);
  pinMode(IO14, INPUT_PULLDOWN);
  pinMode(IO12, INPUT_PULLDOWN);

  dht.begin();  // Initialize the DHT sensor
  SoftTimer.add(&readRelays);  // Add the task to the timer
}

// Read the temperature and humidity, then send it as JSON
void readTemperatureHumidity()
{
  float humidity = dht.readHumidity();  // Get humidity
  float temperature = dht.readTemperature();  // Get temperature in Celsius

  // Check if the readings are valid
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Create a JSON object
  DynamicJsonDocument doc(1024);  // Use DynamicJsonDocument with appropriate size

  // Add the sensor data to the JSON object
  doc["sensor_id"] = "0x01";  // Sensor ID for temperature and humidity
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = String(millis());

  // Serialize JSON object to String
  String jsonData;
  serializeJson(doc, jsonData);

  // Print the JSON data to Serial Monitor
  Serial.println("Sending data: ");
  Serial.println(jsonData);

  // Send the POST request to Flask API
  if (ETH.linkUp())
  {
    Serial.println("Connecting to Flask API...");
    http.begin(host);  // Start the HTTP connection
    http.addHeader("Content-Type", "application/json");  // Set content-type as JSON

    int httpResponseCode = http.POST(jsonData);  // Send the POST request with JSON payload

    // Check the HTTP response code
    if (httpResponseCode == 200)
    {
      String response = http.getString();  // Get the response from the server
      Serial.println("Response Code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    }
    else
    {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    // End the HTTP connection
    http.end();
  }
  else
  {
    Serial.println("Error in Ethernet connection");
  }
}

// Read the state of the relays
void readState(int pin, int sensorid)
{
  int state = digitalRead(pin);

  // Create a JSON object
  DynamicJsonDocument doc(1024);  // Use DynamicJsonDocument with appropriate size

  // Add the data to the JSON object for POST
  doc["sensor_id"] = sensorid;
  doc["state"] = state;  // state could be 1 or 0 based on relay status (on/off)
  doc["timestamp"] = String(millis());

  // Serialize JSON object to String
  String jsonData;
  serializeJson(doc, jsonData);

  // Print the JSON data to Serial Monitor
  Serial.println("Sending data: ");
  Serial.println(jsonData);

  // Send the POST request to Flask API
  if (ETH.linkUp())
  {
    Serial.println("Connecting to Flask API...");
    http.begin(host);  // Start the HTTP connection
    http.addHeader("Content-Type", "application/json");  // Set content-type as JSON

    int httpResponseCode = http.POST(jsonData);  // Send the POST request with JSON payload

    // Check the HTTP response code
    if (httpResponseCode == 200)
    {
      String response = http.getString();  // Get the response from the server
      Serial.println("Response Code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    }
    else
    {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    // End the HTTP connection
    http.end();
  }
  else
  {
    Serial.println("Error in Ethernet connection");
  }
}
