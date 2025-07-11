from flask import request, jsonify
from time import sleep
from datetime import datetime
import logging
import os
import json

from network_utils.auth import authenticate_request
from network_utils.sensor_storage import store_sensor_data
from network_utils.fusion_utils import get_latest_fused_temperature_humidity, get_fused_values_by_sensors
from network_utils.actions import action_based_on_sensor
from network_utils.constants import soil_sensor_1id, soil_sensor_2id
from database_setup import SessionLocal, Actuator
from network_utils.user_control import handle_manual_control
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

### ⬛⬛⬛ START NEW ⬛⬛⬛
# Load manual control state
MANUAL_STATE_FILE = os.path.join("network_utils", "manual_control_state.json")

def load_manual_control_state():
    try:
        with open(MANUAL_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read manual_control_state.json: {e}")
        return {
            "manual_mode": False,
            "ventilation_actuator_state": "off",
            "irrigation_actuator_state": "off"
        }
### ⬛⬛⬛ END NEW ⬛⬛⬛

def receive_sensor_data(request):
    if not authenticate_request(request):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        print(f"Recived paylaod: {data}")
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        time = datetime.utcnow()
        device_id = data.get('DeviceID')
        device_name = data.get('DeviceName')
        actuator_id = data.get('ActuatorID')
        actuator_status = data.get('ActuatorState')
        sensor_ids = data.get("SensorID", [])

        temperatures = data.get("temperature", [])
        filtered_temperatures = data.get("filtered_temperature", [])
        humidities = data.get("humidity", [])
        filtered_humidities = data.get("filtered_humidity", [])
        soil_moistures = data.get("soil_moisture", [])
        filtered_soil_moistures = data.get("filtered_soil_moisture", [])

        with SessionLocal() as session:
            for i, sensor_id in enumerate(sensor_ids):
                if i < len(temperatures) and i < len(filtered_temperatures):
                    if temperatures[i] > 0 and filtered_temperatures[i] > 0:
                        store_sensor_data(session, device_id, device_name, sensor_id,
                                          temperature=temperatures[i],
                                          filtered_temperature=filtered_temperatures[i],
                                          timestamp=time)

                if i < len(humidities) and i < len(filtered_humidities):
                    if humidities[i] > 0 and filtered_humidities[i] > 0:
                        store_sensor_data(session, device_id, device_name, sensor_id,
                                          humidity=humidities[i],
                                          filtered_humidity=filtered_humidities[i],
                                          timestamp=time)

                if i < len(soil_moistures) and i < len(filtered_soil_moistures):
                    if soil_moistures[i] > 0 and filtered_soil_moistures[i] > 0:
                        store_sensor_data(session, device_id, device_name, sensor_id,
                                          soil_moisture=soil_moistures[i],
                                          filtered_soil_moisture=filtered_soil_moistures[i],
                                          timestamp=time)

                logger.info(f"Received data from DeviceID: {device_id}, SensorID: {sensor_id}")

            # Handle actuator state
            if actuator_id is not None and actuator_status is not None:
                actuator = session.query(Actuator).filter(Actuator.ActuatorID == actuator_id).first()
                if actuator:
                    actuator.Status = actuator_status
                    actuator.LastUpdated = time
                    logger.info(f"Updated Actuator {actuator_id} to {actuator_status}")
                    session.commit()
                else:
                    try:
                        new_actuator = Actuator(
                            ActuatorID=actuator_id,
                            ActuatorName=f"Auto_Actuator_{actuator_id}",
                            Status=actuator_status,
                            UserID=5000,  # Automatic control
                            DeviceID=device_id,
                            LastUpdated=time
                        )
                        session.add(new_actuator)
                        logger.info(f"Created new Actuator with ID {actuator_id} and status {actuator_status}")
                    except Exception as e:
                        session.rollback()
                        logger.warning(f"Failed to insert new actuator — error: {e}")

            ### ⬛⬛⬛ START NEW ⬛⬛⬛
            manual_state = load_manual_control_state()

            latest = get_latest_fused_temperature_humidity(session)
            soil_data = get_fused_values_by_sensors(session, soil_sensor_1id, soil_sensor_2id)
            avg_soil = sum(soil_data.values()) / len(soil_data) if soil_data else None

            session.commit()            
            if manual_state.get("manual_mode") is True:
                handle_manual_control()
                actions = []
                if manual_state.get("ventilation_actuator_state", "off") == "off":
                    actions.append("Ventilation_OFF")
                if manual_state.get("ventilation_actuator_state", "on") == "on":
                    actions.append("Ventilation_ON")
                if manual_state.get("irrigation_actuator_state", "on") == "on":
                    actions.append("Irrigation_ON")
                if manual_state.get("irrigation_actuator_state", "off") == "off":
                    actions.append("Irrigation_OFF")
                

                logger.info("[MODE] Manual mode active. Sending manual actuator states.")
                print("Belo")
                print({
                    "status": "success",
                    "action": ", ".join(actions),
                    "temperature": latest.get("temperature"),
                    "humidity": latest.get("humidity"),
                    "soil_moisture": avg_soil
                })
                return jsonify({
                    "status": "success",
                    "action": ", ".join(actions),
                    "temperature": latest.get("temperature"),
                    "humidity": latest.get("humidity"),
                    "soil_moisture": avg_soil
                }), 200
            ### ⬛⬛⬛ END NEW ⬛⬛⬛

            # Else: Automatic control
            action_result = action_based_on_sensor()


        sleep(5)  # Optional delay

        return jsonify({
            "status": "success",
            "action": action_result,
            "temperature": latest.get("temperature"),
            "humidity": latest.get("humidity"),
            "soil_moisture": avg_soil
        }), 200

    except Exception as e:
        logger.error(f"Failed to receive/process sensor data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
