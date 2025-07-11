from database_setup import Device, Sensor
from sqlalchemy.orm import Session

def get_or_create_device(session: Session, device_id, device_name):
    print("[DEBUG] device_utils.py/get_or_create_device loaded successfully.")
    device = session.query(Device).filter_by(DeviceID=device_id).first()
    if not device:
        device = Device(DeviceID=device_id, DeviceName=device_name, Location="Unknown", Status="Active")
        session.add(device)
        session.commit()
        session.refresh(device)
    print("[DEBUG] device_utils.py/get_or_create_device[WORKED].")
    return device

def get_or_create_sensor(session: Session, sensor_id, device_id, sensor_type):
    print("[DEBUG] device_utils.py/get_or_create_sensor loaded successfully.")
    
    sensor = session.query(Sensor).filter_by(SensorID=sensor_id).first()
    if not sensor:
        # Create new sensor if none exists with this SensorID
        sensor = Sensor(SensorID=sensor_id, DeviceID=device_id, SensorType=sensor_type, Location="Unknown", Status="Active")
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
    else:
        # Optionally update sensor_type or other fields if different
        if sensor.SensorType != sensor_type:
            sensor.SensorType = sensor_type
            session.commit()
    
    print("[DEBUG] device_utils.py/get_or_create_sensor[WORKED].")
    return sensor

