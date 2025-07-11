from datetime import datetime
from database_setup import SensorData, KalmanFilterFusionData
from .device_utils import get_or_create_device, get_or_create_sensor

def store_sensor_value(session, sensor, value, time):
    print("[DEBUG] sensor_storage.py/store_sensor_value loaded successfully.")
    session.add(SensorData(SensorID=sensor.SensorID, Value=value, Timestamp=time))
    print("[DEBUG] sensor_storage.py/store_sensor_value [WORKED].")

def store_sensor_fused_value(session, sensor, value, time):
    print("[DEBUG] sensor_storage.py/store_sensor_fused_value loaded successfully.")
    session.add(KalmanFilterFusionData(SensorID=sensor.SensorID, FusedValue=value, Timestamp=time))
    print("[DEBUG] sensor_storage.py/store_sensor_fused_value [WORKED].")

def store_sensor_data(session, device_id, device_name, sensor_id,
                      temperature=None, filtered_temperature=None,
                      humidity=None, filtered_humidity=None,
                      soil_moisture=None, filtered_soil_moisture=None, timestamp=None):
    get_or_create_device(session, device_id, device_name)
    print("[DEBUG] sensor_storage.py/store_sensor_data loaded successfully.")
    if temperature is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "temperature")
        store_sensor_value(session, sensor, temperature, timestamp)
    if filtered_temperature is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "temperature")
        store_sensor_fused_value(session, sensor, filtered_temperature, timestamp)
    if humidity is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "humidity")
        store_sensor_value(session, sensor, humidity, timestamp)
    if filtered_humidity is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "humidity_filtered")
        store_sensor_fused_value(session, sensor, filtered_humidity, timestamp)
    if soil_moisture is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "soil_moisture")
        store_sensor_value(session, sensor, soil_moisture,timestamp)
    if filtered_soil_moisture is not None:
        sensor = get_or_create_sensor(session, sensor_id, device_id, "soil_moisture_filtered")
        store_sensor_fused_value(session, sensor, filtered_soil_moisture, timestamp)
    session.commit()
    print("[DEBUG] sensor_storage.py/store_sensor_data [WORKED].")