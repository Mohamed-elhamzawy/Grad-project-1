from flask import request, jsonify
from database_setup import SessionLocal, SensorData, Device,UserInteraction
from datetime import datetime

# Device (Microcontrollers) authentication credentials for sending sensor data to the server
credentials = {
    "esp_Temp_humid_1": "esp_password",
    "esp_Soil_moisture_1": "esp_password"
}

def action_based_on_sensor(DeviceName, temperature=0, humidity=0, soil_moisture=0):
    session = SessionLocal()
    try:
        if DeviceName == "esp_Temp_humid_1" and temperature > 30:
            session.add(UserInteraction(DeviceID=11, UserID=5000, Action="blink_led", Timestamp=datetime.utcnow()))
            session.commit()
            return "blink_led"
        
        elif DeviceName == "esp_Soil_moisture_1" and soil_moisture > 30:
            session.add(UserInteraction(DeviceID=12, UserID=5000, Action="blink_led", Timestamp=datetime.utcnow()))
            session.commit()
            return "blink_led"
        
        return "no_action"

    finally:
        session.close()


    
def store_sensor_data(device_id, DeviceName, temperature=None, humidity=None, soil_moisture=None):
    session = SessionLocal()

    # Ensure device exists in the database
    device = session.query(Device).filter_by(DeviceID=device_id).first()
    if not device:
        device = Device(DeviceID=device_id, DeviceName=DeviceName, Type="ESP32", Location="Unknown", Status="Active")
        session.add(device)
        session.commit()
        session.refresh(device)  # Ensure we have the latest DeviceID

    # Store sensor readings for the specific device ID received from ESP
    if temperature is not None and device_id in {1, 2, 3}:
        session.add(SensorData(DeviceID=device_id, SensorType="temperature", Value=temperature, Timestamp=datetime.utcnow()))

    if humidity is not None and device_id in {4, 5, 6}:
        session.add(SensorData(DeviceID=device_id, SensorType="humidity", Value=humidity, Timestamp=datetime.utcnow()))

    if soil_moisture is not None and device_id in {7, 8}:
        session.add(SensorData(DeviceID=device_id, SensorType="soil_moisture", Value=soil_moisture, Timestamp=datetime.utcnow()))

    session.commit()
    session.close()

def receive_sensor_data(request):
    # Get Authorization header
    auth = request.authorization
    if not auth or credentials.get(auth.username) != auth.password:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        device_id = data.get('DeviceID')  # This is an integer
        DeviceName = data.get('DeviceName')  # This is a string
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        soil_moisture = data.get('soil_moisture')  # Fixed key

        if not device_id or not DeviceName:
            return jsonify({"error": "Missing 'DeviceID' or 'DeviceName' in payload"}), 400

        print(f"Received JSON payload: {data}")

        # Store the data in the database
        store_sensor_data(device_id, DeviceName, temperature, humidity, soil_moisture)

        # Determine action based on sensor data
        action = action_based_on_sensor(DeviceName, temperature, humidity, soil_moisture)

        response = {"DeviceName": DeviceName, "action": action}
        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
