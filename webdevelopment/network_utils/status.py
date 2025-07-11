from flask import Blueprint, render_template, jsonify
from .fusion_utils import get_fused_values_by_sensors
from database_setup import SessionLocal, WeightedAverageFusionData
from .constants import soil_sensor_1id, soil_sensor_2id

status_bp = Blueprint('status', __name__)

@status_bp.route("/status")
def status_page():
    return render_template("index.html")

@status_bp.route("/api/latest-fused-values")
def latest_fused_values():
    temperature = None
    humidity = None
    soil_moisture = None

    try:
        with SessionLocal() as session:
            # --- Latest Soil Moisture ---
            result = get_fused_values_by_sensors(session, soil_sensor_1id, soil_sensor_2id)
            soil1 = result.get(soil_sensor_1id)
            soil2 = result.get(soil_sensor_2id)

            valid_soil_values = [v for v in [soil1, soil2] if v is not None and 0 <= v <= 5000]
            if valid_soil_values:
                soil_moisture = sum(valid_soil_values) / len(valid_soil_values)
            else:
                print("[WARNING] No valid soil moisture readings found.")

            # --- Latest Temperature ---
            temp_record = session.query(WeightedAverageFusionData)\
                .filter(WeightedAverageFusionData.SensorType == "temperature")\
                .order_by(WeightedAverageFusionData.Timestamp.desc())\
                .first()

            if temp_record:
                temperature = temp_record.FusedValue
            else:
                print("[WARNING] No temperature data found.")

            # --- Latest Humidity ---
            hum_record = session.query(WeightedAverageFusionData)\
                .filter(WeightedAverageFusionData.SensorType == "humidity")\
                .order_by(WeightedAverageFusionData.Timestamp.desc())\
                .first()

            if hum_record:
                humidity = hum_record.FusedValue
            else:
                print("[WARNING] No humidity data found.")

    except Exception as e:
        print(f"[ERROR] Failed to fetch latest fused values: {e}")

    return jsonify({
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture
    })
