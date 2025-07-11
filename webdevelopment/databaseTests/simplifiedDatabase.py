from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from datetime import datetime

#  SQLite Database Connection
DATABASE_URL = "sqlite:///greenhouse.db"
engine = create_engine(DATABASE_URL, echo=True)  # `echo=True` shows SQL logs

#  Base Model
class Base(DeclarativeBase):
    pass

#  Devices Table
class Device(Base):
    __tablename__ = "devices"

    DeviceID = Column(Integer, primary_key=True)
    DeviceName = Column(String(50), nullable=False)
    Location = Column(String(100))
    Status = Column(String(20))  # e.g., "Active", "Inactive"
    Type = Column(String(50))  # e.g., "ESP32", "Raspberry Pi"

    sensor_data = relationship("SensorData", back_populates="device")
    user_interactions = relationship("UserInteraction", back_populates="device")

#  SensorData Table
class SensorData(Base):
    __tablename__ = "sensor_data"

    DataID = Column(Integer, primary_key=True)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"))
    Timestamp = Column(DateTime, default=datetime.utcnow)
    SensorType = Column(String(50))  # e.g., "temperature", "humidity"
    Value = Column(Float)  # Sensor reading value

    device = relationship("Device", back_populates="sensor_data")

#  UserInteractions Table
class UserInteraction(Base):
    __tablename__ = "user_interactions"

    InteractionID = Column(Integer, primary_key=True)
    UserID = Column(Integer)  # Assuming users are stored elsewhere
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"))
    Action = Column(String(20), nullable=False)  # e.g., "Turn On", "Turn Off"
    Timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="user_interactions")

#  Create Tables in SQLite
Base.metadata.create_all(engine)

print("\n Greenhouse database structure created successfully!")
