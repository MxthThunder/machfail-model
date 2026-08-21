"""Pydantic request and response schemas for validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Ingest Schemas (ESP32 -> Backend)
# ==========================================

class MotorSensorDataIn(BaseModel):
    """Schema for live telemetry payload received from ESP32."""
    motor_id: str = Field(..., description="Unique motor identifier, e.g. M001")
    status: str = Field(..., description="Motor operational status (e.g. 'ON', 'OFF')")
    temperature: float = Field(..., description="Temperature from DHT22 in degrees Celsius")
    humidity: float = Field(..., description="Relative humidity from DHT22 in percentage")
    ir: int = Field(..., description="IR Sensor digital status (0 or 1)")
    acs_adc: float = Field(..., description="Raw ADC reading from ACS712 current sensor")
    current: float = Field(..., description="Calibrated current in Amperes")
    mpu_x: float = Field(..., description="MPU6050 X-axis acceleration in g")
    mpu_y: float = Field(..., description="MPU6050 Y-axis acceleration in g")
    mpu_z: float = Field(..., description="MPU6050 Z-axis acceleration in g")
    total_acceleration: float = Field(..., description="Total acceleration vector magnitude")
    vibration: float = Field(..., description="Calculated vibration value abs(total_accel - 1.0)")
    vibration_level: str = Field(..., description="Classified vibration level: LOW, MEDIUM, HIGH")
    
    # Optional / Future Expandable fields
    voltage: Optional[float] = Field(None, description="Motor supply voltage if sensor present (nullable)")
    esp32_ip: Optional[str] = Field(None, description="ESP32 local network IP address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "motor_id": "M001",
                "status": "ON",
                "temperature": 42.5,
                "humidity": 62.2,
                "ir": 1,
                "acs_adc": 1850,
                "current": 2.40,
                "mpu_x": 0.259,
                "mpu_y": -0.965,
                "mpu_z": -0.062,
                "total_acceleration": 1.021,
                "vibration": 0.021,
                "vibration_level": "LOW"
            }
        }
    )


class MotorDataIngestResponse(BaseModel):
    """Response returned to ESP32 upon successful ingestion."""
    success: bool = True
    message: str = "Motor data received"
    motor_id: str
    timestamp: str


# ==========================================
# Query & Dashboard Schemas
# ==========================================

class MotorLatestDataResponse(BaseModel):
    """Response schema for latest motor telemetry."""
    motor_id: str
    status: str
    temperature: float
    humidity: float
    ir: int
    acs_adc: float
    current: float
    mpu_x: float
    mpu_y: float
    mpu_z: float
    total_acceleration: float
    vibration: float
    vibration_level: str
    voltage: Optional[float] = None
    esp32_ip: Optional[str] = None
    received_at: str


class MotorStatusResponse(BaseModel):
    """Response schema for motor online status & runtime."""
    motor_id: str
    status: str
    online: bool
    last_seen: Optional[str] = None
    runtime_seconds: float = 0.0


class MotorHistoryRecord(BaseModel):
    """Individual record inside historical query response."""
    id: int
    motor_id: str
    status: str
    temperature: float
    humidity: float
    ir: int
    acs_adc: float
    current: float
    mpu_x: float
    mpu_y: float
    mpu_z: float
    total_acceleration: float
    vibration: float
    vibration_level: str
    voltage: Optional[float] = None
    esp32_ip: Optional[str] = None
    timestamp: str


class MotorHistoryResponse(BaseModel):
    """Response schema for historical telemetry."""
    motor_id: str
    count: int
    records: List[MotorHistoryRecord]


# ==========================================
# Motor Control & Polling Schemas
# ==========================================

class MotorControlRequest(BaseModel):
    """Request schema for initiating motor ON/OFF control."""
    motor_id: str = Field(..., description="Target motor ID, e.g. M001")
    command: str = Field(..., description="Requested state: 'ON' or 'OFF'")


class MotorControlResponse(BaseModel):
    """Response acknowledging command queueing without falsely asserting physical state."""
    motor_id: str
    requested_command: str
    actual_status: str
    command_status: str = "PENDING"
    command_id: str


class PendingCommandResponse(BaseModel):
    """Response for ESP32 when polling for pending commands."""
    motor_id: str
    command: Optional[str] = None
    command_id: Optional[str] = None
    has_pending_command: bool = False
    created_at: Optional[str] = None


class CommandAckRequest(BaseModel):
    """Schema for ESP32 to acknowledge execution of a command."""
    motor_id: str
    command_id: str
    status: str = Field("EXECUTED", description="Execution result: 'EXECUTED' or 'FAILED'")


class CommandAckResponse(BaseModel):
    """Response returned upon command acknowledgement."""
    success: bool = True
    message: str
    motor_id: str
    command_id: str
    acknowledged_at: str


# ==========================================
# Health Check Schema
# ==========================================

class HealthResponse(BaseModel):
    """System health check response."""
    status: str = "ok"
    service: str = "motor-monitoring-backend"
    timestamp: str
