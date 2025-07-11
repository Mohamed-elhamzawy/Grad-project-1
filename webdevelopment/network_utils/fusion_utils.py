from sqlalchemy import desc
from database_setup import KalmanFilterFusionData, WeightedAverageFusionData

def get_fused_values_by_sensors(session, *sensor_ids):
    print("[DEBUG] fusion_utils.py/get_fused_values_by_sensors loaded successfully.")
    print(f"[DEBUG] fusion_utils.py/get_fused_values_by_sensors called with sensor_ids: {sensor_ids}")
    fused = {}
    for sensor_id in sensor_ids:
        fusion = session.query(KalmanFilterFusionData).filter_by(SensorID=sensor_id).order_by(desc(KalmanFilterFusionData.Timestamp)).first()
        if fusion:
            fused[sensor_id] = fusion.FusedValue
    print("[DEBUG] fusion_utils.py/get_fused_values_by_sensors [WORKED].")
    return fused

def get_latest_fused_temperature_humidity(session):
    print("[DEBUG] fusion_utils.py/get_latest_fused_temperature_humidity loaded successfully.")
    temp = session.query(WeightedAverageFusionData).filter_by(SensorType="temperature").order_by(desc(WeightedAverageFusionData.Timestamp)).first()
    hum = session.query(WeightedAverageFusionData).filter_by(SensorType="humidity").order_by(desc(WeightedAverageFusionData.Timestamp)).first()
    print("[DEBUG] fusion_utils.py/get_latest_fused_temperature_humidity [WORKED].")
    return {
        "temperature": temp.FusedValue if temp else None,
        "humidity": hum.FusedValue if hum else None
    }
