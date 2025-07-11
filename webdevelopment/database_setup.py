from sqlalchemy import (
    create_engine, Column, Integer, Float, String, DateTime,
    ForeignKey, Boolean, Index
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

# ──────────────────────────── Database Connection ────────────────────────────
DATABASE_URL = "sqlite:///greenhouse.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,         # 🔧 Ensures connection is alive before each use
    pool_recycle=1800           # 🔁 Recycle connection every 30 minutes
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=True)  # ✅ Forces fresh reads

# ──────────────────────────── Base ────────────────────────────
Base = declarative_base()

# ──────────────────────────── Tables ────────────────────────────

class UserCredentials(Base):
    __tablename__ = "user_credentials"

    UserID = Column(Integer, primary_key=True)
    Username = Column(String(50), nullable=False, unique=True)
    PasswordHash = Column(String(128), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    FullName = Column(String(100))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    IsActive = Column(Boolean, default=True)

    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    actuators = relationship("Actuator", back_populates="user")

    def __repr__(self):
        return f"<UserCredentials(Username={self.Username}, Email={self.Email})>"


class Device(Base):
    __tablename__ = "devices"

    DeviceID = Column(Integer, primary_key=True, autoincrement=False)
    DeviceName = Column(String(50), nullable=False)
    Location = Column(String(100))
    Status = Column(String(20), default="Active")

    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    user_interactions = relationship("UserInteraction", back_populates="device", cascade="all, delete-orphan")
    actuators = relationship("Actuator", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device(Name={self.DeviceName}, Location={self.Location})>"


class Sensor(Base):
    __tablename__ = "sensors"

    SensorID = Column(Integer, primary_key=True, autoincrement=False)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"), nullable=False)
    SensorType = Column(String(50), nullable=False)
    Location = Column(String(100))
    Status = Column(String(20), default="Active")

    device = relationship("Device", back_populates="sensors")
    sensor_data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")
    kalmanFilterFusionData = relationship("KalmanFilterFusionData", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(SensorID={self.SensorID}, Type={self.SensorType}, Location={self.Location})>"


class SensorData(Base):
    __tablename__ = "sensor_data"
    __table_args__ = (
        Index("ix_sensor_data_sensorid_timestamp", "SensorID", "Timestamp"),
    )

    DataID = Column(Integer, primary_key=True)
    SensorID = Column(Integer, ForeignKey("sensors.SensorID"), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    Value = Column(Float, nullable=False)

    sensor = relationship("Sensor", back_populates="sensor_data")

    def __repr__(self):
        return f"<SensorData(SensorID={self.SensorID}, Value={self.Value})>"


class KalmanFilterFusionData(Base):
    __tablename__ = "kalman_filter_fusion"

    FusionID = Column(Integer, primary_key=True)
    SensorID = Column(Integer, ForeignKey("sensors.SensorID"), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    FusedValue = Column(Float, nullable=False)

    sensor = relationship("Sensor", back_populates="kalmanFilterFusionData")

    def __repr__(self):
        return f"<KalmanFusion(SensorID={self.SensorID}, Value={self.FusedValue})>"


class WeightedAverageFusionData(Base):
    __tablename__ = "weighted_average_fusion"

    FusionID = Column(Integer, primary_key=True)
    SensorType = Column(String(50), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    FusedValue = Column(Float, nullable=False)

    def __repr__(self):
        return f"<WeightedFusion(SensorType={self.SensorType}, Value={self.FusedValue})>"


class Actuator(Base):
    __tablename__ = "actuators"

    ActuatorID = Column(Integer, primary_key=True)
    ActuatorName = Column(String(50), nullable=False, unique=True)
    Status = Column(String(20), nullable=False, default="Inactive")
    LastUpdated = Column(DateTime, default=datetime.utcnow)
    UserID = Column(Integer, ForeignKey("user_credentials.UserID"))
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"))

    interactions = relationship("UserInteraction", back_populates="actuator")
    user = relationship("UserCredentials", back_populates="actuators")
    device = relationship("Device", back_populates="actuators")

    def __repr__(self):
        return f"<Actuator(Name={self.ActuatorName}, Status={self.Status})>"


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    InteractionID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey("user_credentials.UserID"), nullable=False)
    DeviceID = Column(Integer, ForeignKey("devices.DeviceID"), nullable=False)
    ActuatorID = Column(Integer, ForeignKey("actuators.ActuatorID"))
    Action = Column(String(20), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserCredentials", back_populates="interactions")
    device = relationship("Device", back_populates="user_interactions")
    actuator = relationship("Actuator", back_populates="interactions")

    def __repr__(self):
        return f"<UserInteraction(UserID={self.UserID}, DeviceID={self.DeviceID}, Action={self.Action})>"

# ──────────────────────────── Create All Tables ────────────────────────────
Base.metadata.create_all(engine)
