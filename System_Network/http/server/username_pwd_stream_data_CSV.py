from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Define valid credentials
credentials = {
    "esp_Temp_humid_1": "esp_password",
    "esp_Soil_moisture_1": "esp_password"
}

# Path to store received data
CSV_FILE_esp_Temp_humid_1 = r"D:/studies/collage/Grad Project/System_Network/http/data/esp_Temp_humid_1.csv"
CSV_FILE_esp_Soil_moisture_1 = r"D:/studies/collage/Grad Project/System_Network/http/data/esp_Soil_moisture_1.csv"

# Ensure the CSV file exists with headers

if not os.path.exists(CSV_FILE_esp_Temp_humid_1):
    with open(CSV_FILE_esp_Temp_humid_1, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["device_id", "temperature", "humidity", "timestamp"])


def save_sensor_data(device_id, temperature, humidity, timestamp, soil_moisture):

    """Save data to CSV file."""

    if not timestamp:  # Use current time if no timestamp is provided

        timestamp = datetime.now().isoformat()

    if device_id == "esp_Temp_humid_1":

        with open(CSV_FILE_esp_Temp_humid_1, mode='a', newline='') as file:

            writer = csv.writer(file)
            writer.writerow([device_id, temperature, humidity, timestamp])

    if device_id == "esp_Soil_moisture_1":
        
        with open(CSV_FILE_esp_Soil_moisture_1, mode='a', newline='') as file:

            writer = csv.writer(file)
            writer.writerow([device_id, soil_moisture, timestamp])


def action_based_on_sensor(device_id, temperature, humidity, timestamp, soil_moisture):

        if device_id == "esp_Temp_humid_1" and temperature > 30:
            return "blink_led"
        elif device_id == "esp_Soil_moisture_1" and soil_moisture > 30:
            return "blink_led"
        else:
            return "no_action"



@app.route('/receive', methods=['POST'])
def receive_data():
    # Get Authorization header
    auth = request.authorization
    if not auth or credentials.get(auth.username) != auth.password:
        return jsonify({"error": "Unauthorized"}), 401  # Unauthorized

    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        device_id = data.get('device_id')
        temperature = data.get('temperature')
        humidity = data.get('humidity')  # Optional: include humidity if available
        timestamp = data.get('timestamp')  # Optional: include timestamp if provided
        esp_soil_moisture = data.get('Soil_moisture')

        if device_id is None:
            return jsonify({"error": "Missing 'device_id' in payload"}), 400

        print(f"Received JSON payload: {data}")

        # Save data to CSV
        save_sensor_data(device_id, temperature, humidity, timestamp, esp_soil_moisture)

        # take actions based on sensor data
        action = action_based_on_sensor(device_id, temperature, humidity, timestamp, esp_soil_moisture)


        # Respond with action
        response = {"device_id": device_id, "action": action}
        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
