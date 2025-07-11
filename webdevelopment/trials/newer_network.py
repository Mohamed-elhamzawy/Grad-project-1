from flask import request, jsonify
import time
from sqlalchemy import desc
from datetime import datetime
from sqlalchemy.orm import Session
from database_setup import (
    SessionLocal, SensorData, Sensor, Device, UserInteraction,
    Actuator, WeightedAverageFusionData, KalmanFilterFusionData
)
from weightedAverage import process_weighted_fusion

# Authentication credentials for devices
credentials = {
    "Ventilation_System_ESP": "password",
    "Irrigation_System_ESP": "password",
    "web_control": "web_password"
}

# Constants
DEFAULT_USER_ID = 5000  # Server user
TEMP_THRESHOLD = 30
HUM_THRESHOLD = 40
SOIL_MOISTURE_THRESHOLD = 30

TEMP_SENSOR_IDS = [2099, 2092, 3093]
HUM_SENSOR_IDS = [2091, 2034, 3027]
WEIGHTS = [0.5, 0.3, 0.2]

# Actuator Names
INTAKE_SHUTTER = "intake_shutter"
WATER_PUMP = "water_pump"
VENTILATION_FAN = "ventilation_fan"

# Device IDs
Ventilation_System_ESP_ID = 2000
Irrigation_System_ESP_ID = 3000

soil_sensor_1id = 2005
soil_sensor_2id = 3002


def get_fused_values_by_sensors(session: Session, *sensor_ids: int):
    fused_values = {}

    if not sensor_ids:
        return fused_values  # No IDs provided → return empty

    for sensor_id in sensor_ids:
        if sensor_id is None:
            continue
        fusion = (
            session.query(KalmanFilterFusionData)
            .filter_by(SensorID=sensor_id)
            .order_by(desc(KalmanFilterFusionData.Timestamp))
            .first()
        )
        if fusion:
            fused_values[sensor_id] = fusion.FusedValue

    return fused_values


def log_user_action(session, device_id, action, user_id, actuator_id):
    session.add(UserInteraction(
        DeviceID=device_id,
        Action=action,
        UserID=user_id,
        ActuatorID=actuator_id,
        Timestamp=datetime.utcnow()
    ))


def control_actuator(session, actuator_name, status, user_id):
    actuator = session.query(Actuator).filter_by(ActuatorName=actuator_name).first()
    if not actuator:
        actuator = Actuator(
            ActuatorName=actuator_name,
            Status=status,
            LastUpdated=datetime.utcnow(),
            UserID=user_id
        )
        session.add(actuator)
    else:
        if actuator.Status != status:
            actuator.Status = status
            actuator.LastUpdated = datetime.utcnow()
            actuator.UserID = user_id
            log_user_action(
                session,
                device_id=actuator.ActuatorID,
                action=f"{actuator_name}_{status.lower()}",
                user_id=user_id,
                actuator_id=actuator.ActuatorID
            )
    session.commit()
    return actuator


def get_latest_fused_temperature_humidity(session):
    latest_temp = session.query(WeightedAverageFusionData).filter_by(
        SensorType="temperature").order_by(desc(WeightedAverageFusionData.Timestamp)).first()
    latest_hum = session.query(WeightedAverageFusionData).filter_by(
        SensorType="humidity").order_by(desc(WeightedAverageFusionData.Timestamp)).first()

    return {
        "temperature": latest_temp.FusedValue if latest_temp else None,
        "humidity": latest_hum.FusedValue if latest_hum else None
    }


def action_based_on_sensor(user_id=DEFAULT_USER_ID):
    with SessionLocal() as session:
        result = get_fused_values_by_sensors(session, soil_sensor_1id, soil_sensor_2id)
        soil1 = result.get(soil_sensor_1id)
        soil2 = result.get(soil_sensor_2id)

        soil_moisture = None
        if soil1 is not None and soil2 is not None:
            average = (soil1 + soil2) / 2
            if 0 <= average <= 100:
                soil_moisture = average
        elif soil1 is not None:
            if 0 <= soil1 <= 100:
                soil_moisture = soil1
        elif soil2 is not None:
            if 0 <= soil2 <= 100:
                soil_moisture = soil2
        # Else → soil_moisture stays None

        temperature=process_weighted_fusion(sensor_ids=TEMP_SENSOR_IDS, weights=WEIGHTS, sensor_type="Temperature")

        # Call for humidity
        humidity=process_weighted_fusion(sensor_ids=HUM_SENSOR_IDS, weights=WEIGHTS, sensor_type="Humidity")

        actions = []

        try:
            if temperature is not None and humidity is not None:
                if temperature > TEMP_THRESHOLD or humidity > HUM_THRESHOLD:
                    control_actuator(session, VENTILATION_FAN, "on", user_id)
                    control_actuator(session, INTAKE_SHUTTER, "on", user_id)
                    actions.append("Ventilation_ON")
                elif temperature < TEMP_THRESHOLD and humidity < HUM_THRESHOLD:
                    control_actuator(session, VENTILATION_FAN, "off", user_id)
                    control_actuator(session, INTAKE_SHUTTER, "off", user_id)
                    actions.append("Ventilation_OFF")

            if soil_moisture is not None:
                if soil_moisture < SOIL_MOISTURE_THRESHOLD:
                    control_actuator(session, WATER_PUMP, "on", user_id)
                    actions.append("Irrigation_ON")
                else:
                    control_actuator(session, WATER_PUMP, "off", user_id)
                    actions.append("Irrigation_OFF")

            session.commit()
            return ", ".join(actions) if actions else "none"
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Failed to perform action: {e}")
            return "error"



def get_or_create_device(session, device_id, device_name):
    device = session.query(Device).filter_by(DeviceID=device_id).first()
    if not device:
        device = Device(DeviceID=device_id, DeviceName=device_name, Location="Unknown", Status="Active")
        session.add(device)
        session.commit()
        session.refresh(device)
    return device


def get_or_create_sensor(session,sensor_id, device_id, sensor_type):
    sensor = session.query(Sensor).filter_by(SensorID=sensor_id, SensorType=sensor_type).first()
    if not sensor:
        sensor = Sensor(SensorID=sensor_id, DeviceID=device_id, SensorType=sensor_type, Location="Unknown", Status="Active")
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
    return sensor


def store_sensor_value(session, sensor, value):
    session.add(SensorData(SensorID=sensor.SensorID, Value=value, Timestamp=datetime.utcnow()))


def store_sensor_data(device_id, device_name,sensor_id,
                      temperature=None, filtered_temperature=None,
                      humidity=None, filtered_humidity=None,
                      soil_moisture=None, filtered_soil_moisture=None):
    with SessionLocal() as session:
        try:
            get_or_create_device(session, device_id, device_name)

            if temperature is not None:
                sensor = get_or_create_sensor(session, device_id, "temperature")
                store_sensor_value(session, sensor, temperature)

            if filtered_temperature is not None:
                sensor = get_or_create_sensor(session, device_id, "temperature_filtered")
                store_sensor_value(session, sensor, filtered_temperature)

            if humidity is not None:
                sensor = get_or_create_sensor(session, device_id, "humidity")
                store_sensor_value(session, sensor, humidity)

            if filtered_humidity is not None:
                sensor = get_or_create_sensor(session, device_id, "humidity_filtered")
                store_sensor_value(session, sensor, filtered_humidity)

            if soil_moisture is not None:
                sensor = get_or_create_sensor(session, device_id, "soil_moisture")
                store_sensor_value(session, sensor, soil_moisture)

            if filtered_soil_moisture is not None:
                sensor = get_or_create_sensor(session, device_id, "soil_moisture_filtered")
                store_sensor_value(session, sensor, filtered_soil_moisture)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Failed to store sensor data: {e}")


def receive_sensor_data(request):
    auth = request.authorization
    if not auth or credentials.get(auth.username) != auth.password:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        device_id = data.get('DeviceID')
        device_name = data.get('DeviceName')
        sensor_id = data.get('SensorID')
        if not device_id or not device_name:
            return jsonify({"error": "Missing DeviceID or DeviceName"}), 400

        temperature = data.get('temperature')
        filtered_temperature = data.get('filtered_temperature')
        humidity = data.get('humidity')
        filtered_humidity = data.get('filtered_humidity')
        soil_moisture = data.get('soil_moisture')
        filtered_soil_moisture = data.get('filtered_soil_moisture')

        store_sensor_data(device_id, device_name,sensor_id,
                          temperature, filtered_temperature,
                          humidity, filtered_humidity,
                          soil_moisture, filtered_soil_moisture)
        
        print(f"[INFO] Received data from DeviceID: {device_id}, SensorID: {sensor_id}")
        # Optional: wait for fusion update to complete if it's not sync
        time.sleep(5)

        action_result = action_based_on_sensor()

        with SessionLocal() as session:
            latest = get_latest_fused_temperature_humidity(session)
            soil_data = get_fused_values_by_sensors(session, soil_sensor_1id, soil_sensor_2id)
            avg_soil = None
            if soil_data:
                values = list(soil_data.values())
                avg_soil = sum(values) / len(values) if values else None

        return jsonify({
            "status": "success",
            "action": action_result,
            "temperature": latest["temperature"],
            "humidity": latest["humidity"],
            "soil_moisture": avg_soil
        }), 200

    except Exception as e:
        print(f"[ERROR] Failed to receive/process sensor data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
