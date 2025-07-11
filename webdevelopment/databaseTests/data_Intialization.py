import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker
from database_setup import (
    Base, engine, SessionLocal,
    UserCredentials, Device, Sensor,
    SensorData, KalmanFilterFusionData,
    Actuator
)

fake = Faker()

# Use same sensor IDs from your fusion logic
TEMP_SENSOR_IDS = [2099, 2092, 3093]
HUM_SENSOR_IDS = [2091, 2034, 3027]
ALL_SENSOR_IDS = TEMP_SENSOR_IDS + HUM_SENSOR_IDS

def create_dummy_user(session: Session):
    user = UserCredentials(
        Username="test_user",
        PasswordHash="hashed_password",
        Email="test@example.com",
        FullName="Test User"
    )
    session.add(user)
    session.flush()  # get UserID for foreign keys
    return user

def create_dummy_devices(session: Session):
    devices = []
    for i in range(1, 4):
        device = Device(
            DeviceID=1000 + i,
            DeviceName=f"Device_{i}",
            Location=fake.city()
        )
        session.add(device)
        devices.append(device)
    session.flush()
    return devices

def create_dummy_sensors(session: Session, devices):
    sensors = []
    sensor_definitions = [
        (TEMP_SENSOR_IDS[0], devices[0], "Temperature"),
        (TEMP_SENSOR_IDS[1], devices[1], "Temperature"),
        (TEMP_SENSOR_IDS[2], devices[2], "Temperature"),
        (HUM_SENSOR_IDS[0], devices[0], "Humidity"),
        (HUM_SENSOR_IDS[1], devices[1], "Humidity"),
        (HUM_SENSOR_IDS[2], devices[2], "Humidity"),
    ]
    for sensor_id, device, sensor_type in sensor_definitions:
        sensor = Sensor(
            SensorID=sensor_id,
            DeviceID=device.DeviceID,
            SensorType=sensor_type,
            Location=device.Location
        )
        session.add(sensor)
        sensors.append(sensor)
    session.flush()
    return sensors

def insert_sensor_data(session: Session, sensors):
    now = datetime.utcnow()
    for sensor in sensors:
        for i in range(3):  # 3 entries per sensor
            timestamp = now - timedelta(minutes=i)
            value = round(random.uniform(20.0, 35.0), 2) if "Temp" in sensor.SensorType else round(random.uniform(30.0, 80.0), 2)

            # Raw sensor data
            sensor_data = SensorData(
                SensorID=sensor.SensorID,
                Timestamp=timestamp,
                Value=value
            )
            session.add(sensor_data)

            # Simulated Kalman output (slightly smoothed)
            kalman_value = round(value + random.uniform(-1.0, 1.0), 2)
            kalman_data = KalmanFilterFusionData(
                SensorID=sensor.SensorID,
                Timestamp=timestamp,
                FusedValue=kalman_value
            )
            session.add(kalman_data)

def create_dummy_actuators(session: Session, user, devices):
    for i, device in enumerate(devices):
        actuator = Actuator(
            ActuatorName=f"Pump_{i+1}",
            Status="Active" if i % 2 == 0 else "Inactive",
            UserID=user.UserID,
            DeviceID=device.DeviceID
        )
        session.add(actuator)

def main():
    Base.metadata.create_all(engine)
    session = SessionLocal()

    try:
        print("[INFO] Populating database with dummy data...")

        user = create_dummy_user(session)
        devices = create_dummy_devices(session)
        sensors = create_dummy_sensors(session, devices)
        insert_sensor_data(session, sensors)
        create_dummy_actuators(session, user, devices)

        session.commit()
        print("[SUCCESS] Database populated successfully.")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to populate database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
