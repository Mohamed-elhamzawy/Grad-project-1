from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from database_setup import engine, Device, SensorData

Session = sessionmaker(bind=engine)
session = Session()

#  Example: Insert multiple temperature readings at once
sensor_readings = [
    {"DeviceID": 1, "SensorType": "humidity", "Value": 21.2},
    {"DeviceID": 2, "SensorType": "humidity", "Value": 22.2},
    {"DeviceID": 3, "SensorType": "humidity", "Value": 23.4},
    {"DeviceID": 4, "SensorType": "humidity", "Value": 24.4},
    {"DeviceID": 5, "SensorType": "temperature", "Value": 42.2},
    {"DeviceID": 6, "SensorType": "temperature", "Value": 41.2},
    {"DeviceID": 7, "SensorType": "temperature", "Value": 43.4},
    {"DeviceID": 8, "SensorType": "temperature", "Value": 45.4},
    {"DeviceID": 9, "SensorType": "soil_moisture", "Value": 50.2},
    {"DeviceID": 10, "SensorType": "soil_moisture", "Value": 54.4}
]


# Convert dictionary list to SQLAlchemy objects
sensor_objects = [SensorData(**reading) for reading in sensor_readings]

#  Bulk insert all rows at once
session.bulk_save_objects(sensor_objects)
session.commit()
session.close()

print("\n Batch data inserted successfully!")
# Compare this snippet from webdevelopment/Initialize_greenhouse_db.py: