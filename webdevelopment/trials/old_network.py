from flask import request, jsonify
from webdevelopment.database_setup import SessionLocal, SensorData, Device, UserInteraction, Actuator, WeightedAverageFusionData
from datetime import datetime
from webdevelopment.weightedAverage import process_weighted_fusion

# Authentication credentials for devices
credentials = {
    "Ventilation_System_ESP ": "password",
    "Irrigation_System_ESP": "password"
}

# Constants
DEFAULT_USER_ID = 5000  # Server user
TEMP_THRESHOLD = 30
HUM_THRESHOLD = 40
SOIL_MOISTURE_THRESHOLD = 30

# Actuator Names
INTAKE_SHUTTER = "intake_shutter"
WATER_PUMP = "water_pump"
VENTILATION_FAN = "ventilation_fan"

# Device Names
Ventilation_System_ESP = 1111
Irrigation_System_ESP = 2222


def log_user_action(session, device_id, action, user_id):
    interaction = UserInteraction(
        DeviceID=device_id,
        Action=action,
        UserID=user_id,
        Timestamp=datetime.utcnow()
    )
    session.add(interaction)


def control_actuator(session, actuator_name, status, user_id):
    actuator = session.query(Actuator).filter_by(ActuatorName=actuator_name).first()
    if not actuator:
        actuator = Actuator(ActuatorName=actuator_name, Status=status, LastUpdated=datetime.utcnow(), UserID=user_id)
        session.add(actuator)
    else:
        actuator.Status = status
        actuator.LastUpdated = datetime.utcnow()
        actuator.UserID = user_id

    # Log who triggered this actuator
    log_user_action(session, device_id=actuator.ActuatorID, action=f"{actuator_name}_{status.lower()}", user_id=user_id)
    return True


def action_based_on_sensor(DeviceName, temperature=0, humidity=0, soil_moisture=0, user_id=DEFAULT_USER_ID):
    session = SessionLocal()
    
    try:
        if  temperature > TEMP_THRESHOLD or humidity > HUM_THRESHOLD:

            control_actuator(session, VENTILATION_FAN, "On", user_id)
            control_actuator(session, INTAKE_SHUTTER, "On", user_id)
            log_user_action(session, Ventilation_System_ESP,"On", user_id)
            log_user_action(session, INTAKE_SHUTTER,"On", user_id)
            action_taken = "VENTILATION_System_on"


        elif soil_moisture < SOIL_MOISTURE_THRESHOLD:
            control_actuator(session, WATER_PUMP, "On", user_id)
            log_user_action(session, Irrigation_System_ESP, "On", user_id)
            action_taken = "Irrigation_System_on"

        session.commit()
        return action_taken

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to perform action: {e}")
        return "error"

    finally:
        session.close()


def store_sensor_data(device_id, DeviceName, temperature=None, filtered_temperature=None, humidity=None, filtered_humidity=None, soil_moisture=None, filtered_soil_moisture= None):
    session = SessionLocal()

    try:
        # Ensure device exists
        device = session.query(Device).filter_by(DeviceID=device_id).first()
        if not device:
            device = Device(DeviceID=device_id, DeviceName=DeviceName, Type="ESP32", Location="Unknown", Status="Active")
            session.add(device)
            session.commit()
            session.refresh(device)

        # Store relevant sensor data
        if temperature is not None and device_id in {1, 2, 3, 4}:
            session.add(SensorData(DeviceID=device_id, SensorType="temperature", Value=temperature, Timestamp=datetime.utcnow()))
        if filtered_temperature is not None and device_id in {1, 2, 3, 4}:
            session.add(SensorData(DeviceID=device_id, FusedValue=temperature, Timestamp=datetime.utcnow()))        
        if humidity is not None and device_id in {5, 6, 7, 8}:
            session.add(SensorData(DeviceID=device_id, SensorType="humidity", Value=humidity, Timestamp=datetime.utcnow()))
        if filtered_humidity is not None and device_id in {5, 6, 7, 8}:
            session.add(SensorData(DeviceID=device_id, FusedValue=temperature, Timestamp=datetime.utcnow())) 
        if soil_moisture is not None and device_id in {9,10}:
            session.add(SensorData(DeviceID=device_id, SensorType="soil_moisture", Value=soil_moisture, Timestamp=datetime.utcnow()))
        if filtered_soil_moisture is not None and device_id in {9,10}:
            session.add(SensorData(DeviceID=device_id, FusedValue=temperature, Timestamp=datetime.utcnow())) 
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to store sensor data: {e}")
    finally:
        session.close()


def receive_sensor_data(request):
    # Basic HTTP Auth
    auth = request.authorization
    if not auth or credentials.get(auth.username) != auth.password:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
        DeviceID = data.get('DeviceID')
        DeviceName = data.get('DeviceName')
        temperature = data.get('temperature')
        filtered_temperature = data.get('filtered_temperature')
        humidity = data.get('humidity')
        filtered_humidity = data.get('filtered_humidity')
        soil_moisture = data.get('soil_moisture')
        filtered_soil_moisture = data.get('filtered_soil_moisture')

        if not DeviceID:
            return jsonify({"error": "Missing 'DeviceID' in payload"}), 400
        if not DeviceName:
            return jsonify({"error": "Missing 'DeviceName' in payload"}), 400

        print(f"Received payload: from {DeviceName}")

        store_sensor_data(DeviceID, DeviceName, temperature, humidity, soil_moisture)

        process_weighted_fusion()


        action = action_based_on_sensor(DeviceName, temperature, humidity, soil_moisture)

        if action == "VENTILATION_System_on":
            return jsonify({"DeviceName": "Ventilation_System_ESP", "action": action})
        
        elif action == "Irrigation_System_on":
            return jsonify({"DeviceName": "Irrigation_System_ESP", "action": action})
        
        elif action == "error":
            return jsonify({"error": "Failed to perform action"}), 500
        
        else:
            return jsonify({"DeviceName": DeviceName, "action": "No action taken"}), 200
        

    except Exception as e:
        print(f"[ERROR] Exception in receive_sensor_data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
