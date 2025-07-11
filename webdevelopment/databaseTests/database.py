from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from datetime import datetime

# ✅ SQLite Database Connection
DATABASE_URL = "sqlite:///greenhouse.db"
engine = create_engine(DATABASE_URL, echo=True)  # `echo=True` shows SQL logs

# ✅ Base Model
class Base(DeclarativeBase):
    pass

# ✅ Devices Table (ESP32, ESP32-CAM, Raspberry Pi)
class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    type = Column(String)  # e.g., "ESP32", "ESP32-CAM", "Raspberry Pi"
    location = Column(String)  # e.g., "Greenhouse Zone 1"

    sensors = relationship("Sensor", back_populates="device")

# ✅ Sensors Table (Temperature, Humidity, Soil Moisture)
class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    type = Column(String)  # e.g., "temperature", "humidity", "soil_moisture"
    unit = Column(String)  # e.g., "°C", "%", "VWC"

    device = relationship("Device", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")

# ✅ Sensor Readings Table
class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sensor = relationship("Sensor", back_populates="readings")

# ✅ Users Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    role = Column(String)  # e.g., "admin", "user"
    email = Column(String, unique=True)

    actions = relationship("UserAction", back_populates="user")

# ✅ User Actions Table
class UserAction(Base):
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)  # e.g., "turn_on_fan", "water_plants"
    action_value = Column(String)  # Any additional info (e.g., duration)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="actions")

# ✅ Weighted Averages Table (For Dashboards)
class WeightedAverage(Base):
    __tablename__ = "weighted_averages"
    
    id = Column(Integer, primary_key=True)
    sensor_type = Column(String)  # "temperature", "humidity", "soil_moisture"
    weighted_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ✅ Create Tables in SQLite
Base.metadata.create_all(engine)

# ✅ Insert Test Data
Session = sessionmaker(bind=engine)
session = Session()

# Adding sample devices
device1 = Device(name="ESP32_1", type="ESP32", location="Greenhouse Zone 1")
session.add(device1)

# Adding sample sensors
sensor1 = Sensor(device=device1, type="temperature", unit="°C")
session.add(sensor1)

# Adding sample sensor reading
reading1 = SensorReading(sensor=sensor1, value=25.6)
session.add(reading1)

# Adding a test user
user1 = User(username="admin", role="admin", email="admin@example.com")
session.add(user1)

# Adding a test user action
action1 = UserAction(user=user1, action_type="water_plants", action_value="5 seconds")
session.add(action1)

# Committing the session
session.commit()
session.close()

print("\n✅ Database setup complete!")
