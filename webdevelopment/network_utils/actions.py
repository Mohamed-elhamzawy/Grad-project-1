from .fusion_utils import get_fused_values_by_sensors
from .actuator_control import control_actuator
from .config_handler import load_config
from weightedAverage import process_weighted_fusion
from database_setup import SessionLocal, WeightedAverageFusionData
from .constants import *


def action_based_on_sensor(user_id=DEFAULT_USER_ID):
    print("[DEBUG] action.py loaded successfully.")

    # Load dynamic thresholds
    config = load_config()
    TEMP_THRESHOLD = config.get("TEMP_THRESHOLD", 27)
    HUM_THRESHOLD = config.get("HUM_THRESHOLD", 80)
    SOIL_MOISTURE_THRESHOLD = config.get("SOIL_MOISTURE_THRESHOLD", 4000)

    with SessionLocal() as session:
        # Get fused soil moisture readings
        result = get_fused_values_by_sensors(session, soil_sensor_1id, soil_sensor_2id)
        soil1 = result.get(soil_sensor_1id)
        soil2 = result.get(soil_sensor_2id)
        soil_moisture = None

        if soil1 is not None and soil2 is not None:
            avg = (soil1 + soil2) / 2
            if 0 <= avg <= 5000:
                soil_moisture = avg
        elif soil1 and 0 <= soil1 <= 5000:
            soil_moisture = soil1
        elif soil2 and 0 <= soil2 <= 5000:
            soil_moisture = soil2
        else:
            print("[WARNING] Invalid soil moisture readings, using None.")

        # Update fusion values
        process_weighted_fusion(sensor_ids=TEMP_SENSOR_IDS, weights=WEIGHTS, sensor_type="temperature")
        process_weighted_fusion(sensor_ids=HUM_SENSOR_IDS, weights=WEIGHTS, sensor_type="humidity")

        # Get latest temperature
        temperature_record = session.query(WeightedAverageFusionData) \
            .filter(WeightedAverageFusionData.SensorType == "temperature") \
            .order_by(WeightedAverageFusionData.Timestamp.desc()) \
            .first()
        temperature = temperature_record.FusedValue if temperature_record else None
        if temperature is None:
            print("[WARNING] No temperature data found.")

        # Get latest humidity
        humidity_record = session.query(WeightedAverageFusionData) \
            .filter(WeightedAverageFusionData.SensorType == "humidity") \
            .order_by(WeightedAverageFusionData.Timestamp.desc()) \
            .first()
        humidity = humidity_record.FusedValue if humidity_record else None
        if humidity is None:
            print("[WARNING] No humidity data found.")

        actions = []

        try:
            # --- VENTILATION CONTROL ---
            if temperature is not None and humidity is not None:
                if temperature > TEMP_THRESHOLD or humidity > HUM_THRESHOLD:
                    control_actuator(session, VENTILATION_FAN, "on", user_id)
                    control_actuator(session, INTAKE_SHUTTER, "on", user_id)
                    actions.append("Ventilation_ON")
                else:
                    control_actuator(session, VENTILATION_FAN, "off", user_id)
                    control_actuator(session, INTAKE_SHUTTER, "off", user_id)
                    actions.append("Ventilation_OFF")


            # --- IRRIGATION CONTROL ---
            if soil_moisture is not None:
                if soil_moisture < SOIL_MOISTURE_THRESHOLD:
                    control_actuator(session, WATER_PUMP, "on", user_id)
                    actions.append("Irrigation_ON")
                else:
                    control_actuator(session, WATER_PUMP, "off", user_id)
                    actions.append("Irrigation_OFF")

            session.commit()
            print("[DEBUG] actions.py [WORKED]")
            print(f"[DEBUG] Thresholds: TEMP={TEMP_THRESHOLD}, HUM={HUM_THRESHOLD}, SOIL={SOIL_MOISTURE_THRESHOLD}")
            print(f"[DEBUG] Readings: TEMP={temperature}, HUM={humidity}, SOIL={soil_moisture}")
            print(f"[DEBUG] Actions performed: {actions}")
            return ", ".join(actions) if actions else "none"

        except Exception as e:
            session.rollback()
            print(f"[ERROR] Failed to perform action: {e}")
            return "error"
