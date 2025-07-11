from sqlalchemy import (
    create_engine, Column, Integer, Float, String, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from datetime import datetime

# Database connection
DATABASE_URL = "sqlite:///greenhouse.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Base class
class Base(DeclarativeBase):
    pass

# Devices Table
class Device(Base):
    __tablename__ = "devices"

    DeviceID = Column(Integer, primary_key=True)
    DeviceName = Column(String(50), nullable=False)
    Location = Column(String(100))
    Status = Column(String(20))  # e.g., "Active", "Inactive"
    Type = Column(String(50))    # e.g., "ESP32", "Raspberry Pi"

    # Relationships
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    sensor_data = relationship("SensorData", secondary="sensors", viewonly=True)
    user_interactions = relationship("UserInteraction", back_populates="device", cascade="all, delete-orphan")
    kalman_fusions = relationship("KalmanFilterFusionData", back_populates="device", cascade="all, delete-orphan")
    weighted_fusions = relationship("WeightedAverageFusionData", back_populates="device", cascade="all, delete-orphan")

# Sensors Table
class Sensor(Base):
    __tablename__ = "sensors"

    SensorID = Column(Integer, primary_key=True)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"), nullable=False)
    SensorType = Column(String(50))  # e.g., "DHT", "SoilMoisture"
    SensorIndex = Column(Integer)    # To distinguish multiple sensors of same type
    Location = Column(String(100))   # e.g., "Top Left"
    Status = Column(String(20), default="Active")

    device = relationship("Device", back_populates="sensors")
    sensor_data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")

# SensorData Table
class SensorData(Base):
    __tablename__ = "sensor_data"

    DataID = Column(Integer, primary_key=True)
    SensorID = Column(Integer, ForeignKey("sensors.SensorID"), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    Value = Column(Float, nullable=False)

    sensor = relationship("Sensor", back_populates="sensor_data")

# UserInteractions Table
class UserInteraction(Base):
    __tablename__ = "user_interactions"

    InteractionID = Column(Integer, primary_key=True)
    UserID = Column(Integer)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"), nullable=False)
    ActuatorID = Column(Integer, ForeignKey("actuators.ActuatorID"))  # Optional, if interaction is with an actuator
    Action = Column(String(20), nullable=False)  # e.g., "Turn On", "Turn Off"
    Timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="user_interactions")

# Kalman Filter Fusion Table
class KalmanFilterFusionData(Base):
    __tablename__ = "kalman_filter_fusion"

    FusionID = Column(Integer, primary_key=True)
    SensorID = Column(Integer, ForeignKey("kalmanFilterFusionData.SensorID"), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    FusedValue = Column(Float, nullable=False)

    
    sensor = relationship("Sensor", back_populates="kalmanFilterFusionData"
                          
# Weighted Average Fusion Table
class WeightedAverageFusionData(Base):
    __tablename__ = "weighted_average_fusion"

    FusionID = Column(Integer, primary_key=True)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"), nullable=False)
    SensorType = Column(String(50))  # Optional
    Timestamp = Column(DateTime, default=datetime.utcnow)
    FusedValue = Column(Float, nullable=False)

    device = relationship("Device", back_populates="weighted_fusions")

# Actuators Table
class Actuator(Base):
    __tablename__ = "actuators"

    ActuatorID = Column(Integer, primary_key=True)
    ActuatorName = Column(String(50), nullable=False, unique=True)
    Status = Column(String(20), nullable=False)  # e.g., "On", "Off"
    LastUpdated = Column(DateTime, default=datetime.utcnow)
    UserID = Column(Integer)  # Refers to the user who last updated it

    def __repr__(self):
        return f"<Actuator(Name={self.ActuatorName}, Status={self.Status})>"

# Create all tables
Base.metadata.create_all(engine)
