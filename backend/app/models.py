"""SQLAlchemy ORM models for Motor Monitoring."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from app.database import Base


def utc_now() -> datetime:
    """Helper returning timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


class MotorReading(Base):
    """Database table for storing time-series sensor telemetry received from ESP32."""
    __tablename__ = "motor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    motor_id = Column(String(32), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    
    # Motor Status & Environmental Sensors
    status = Column(String(16), nullable=False)  # "ON" or "OFF"
    temperature = Column(Float, nullable=False)   # DHT22 (°C)
    humidity = Column(Float, nullable=False)      # DHT22 (%)
    ir = Column(Integer, nullable=False)          # IR Sensor (0 or 1)
    ir_pulses = Column(Integer, nullable=True, default=0)  # Cumulative IR pulse count
    rpm = Column(Float, nullable=True, default=0.0)        # Motor RPM
    
    # Current Sensor (ACS712)
    acs_adc = Column(Float, nullable=False)       # Raw ADC value
    current = Column(Float, nullable=False)       # Current in Amperes
    
    # Accelerometer / Vibration Sensor (MPU6050)
    mpu_x = Column(Float, nullable=False)         # X Acceleration (g)
    mpu_y = Column(Float, nullable=False)         # Y Acceleration (g)
    mpu_z = Column(Float, nullable=False)         # Z Acceleration (g)
    total_acceleration = Column(Float, nullable=False)  # sqrt(x^2 + y^2 + z^2)
    vibration = Column(Float, nullable=False)     # abs(total_accel - 1.0)
    vibration_level = Column(String(16), nullable=False)  # "LOW", "MEDIUM", "HIGH"
    
    # Motor PWM & Optional / Future Expandable fields
    motor_pwm = Column(Integer, nullable=True, default=0)  # Motor PWM Duty (0-255)
    voltage = Column(Float, nullable=True)        # Voltage (Nullable - not faked)
    esp32_ip = Column(String(64), nullable=True)  # ESP32 local IP address

    __table_args__ = (
        Index("ix_motor_id_timestamp", "motor_id", "timestamp"),
    )


class MotorCommand(Base):
    """Database table for tracking queued and executed motor control commands."""
    __tablename__ = "motor_commands"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    command_id = Column(String(64), unique=True, index=True, nullable=False)
    motor_id = Column(String(32), index=True, nullable=False)
    command = Column(String(16), nullable=False)  # "ON" or "OFF"
    status = Column(String(16), default="PENDING", nullable=False)  # PENDING, EXECUTED, REJECTED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=True)
