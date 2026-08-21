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
    ir_pulses: Optional[int] = Field(0, description="Cumulative IR pulses / counts")
    rpm: Optional[float] = Field(0.0, description="Calculated RPM from IR sensor pulses")
    acs_adc: float = Field(..., description="Raw ADC reading from ACS712 current sensor")
    current: float = Field(..., description="Calibrated current in Amperes")
    mpu_x: float = Field(..., description="MPU6050 X-axis acceleration in g")
    mpu_y: float = Field(..., description="MPU6050 Y-axis acceleration in g")
    mpu_z: float = Field(..., description="MPU6050 Z-axis acceleration in g")
    total_acceleration: float = Field(..., description="Total acceleration vector magnitude")
    vibration: float = Field(..., description="Calculated vibration value abs(total_accel - 1.0)")
    vibration_level: str = Field(..., description="Classified vibration level: LOW, MEDIUM, HIGH")
    motor_pwm: Optional[int] = Field(0, description="Motor PWM speed duty cycle (0-255)")
    
    # Optional / Future Expandable fields
    voltage: Optional[float] = Field(None, description="Motor supply voltage if sensor present (nullable)")
    esp32_ip: Optional[str] = Field(None, description="ESP32 local network IP address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "motor_id": "M001",
                "status": "ON",
                "temperature": 33.9,
                "humidity": 69.0,
                "ir": 0,
                "ir_pulses": 5516,
                "rpm": 2945.7,
                "acs_adc": 530,
                "current": 0.08,
                "mpu_x": 0.01,
                "mpu_y": 0.09,
                "mpu_z": -0.46,
                "total_acceleration": 0.47,
                "vibration": 0.53,
                "vibration_level": "HIGH",
                "motor_pwm": 255,
                "voltage": None,
                "esp32_ip": "192.168.1.xxx"
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
    ir_pulses: Optional[int] = 0
    rpm: Optional[float] = 0.0
    acs_adc: float
    current: float
    mpu_x: float
    mpu_y: float
    mpu_z: float
    total_acceleration: float
    vibration: float
    vibration_level: str
    motor_pwm: Optional[int] = 0
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
    ir_pulses: Optional[int] = 0
    rpm: Optional[float] = 0.0
    acs_adc: float
    current: float
    mpu_x: float
    mpu_y: float
    mpu_z: float
    total_acceleration: float
    vibration: float
    vibration_level: str
    motor_pwm: Optional[int] = 0
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
# Motor Condition Analysis Schemas
# ==========================================

class ConditionParameterResult(BaseModel):
    """Detailed classification for an individual physical parameter."""
    value: float
    unit: str
    condition: str
    score: int


class MotorConditionAnalysisRequest(BaseModel):
    """Payload for manual or custom condition analysis."""
    motor_id: str = Field("M001", description="Motor identifier")
    temperature: float = Field(..., description="Temperature in °C")
    rpm: float = Field(..., description="Motor rotational RPM")
    current: float = Field(..., description="Motor current in Amperes")
    vibration: float = Field(..., description="Vibration reading in g")


class MotorConditionAnalysisResponse(BaseModel):
    """Complete rule-based motor condition evaluation response."""
    motor_id: str
    temperature: ConditionParameterResult
    rpm: ConditionParameterResult
    current: ConditionParameterResult
    vibration: ConditionParameterResult
    overall_condition: str
    condition_score: int
    maximum_score: int = 8
    failure_risk: str
    risk_type: str = "Rule-Based Failure Risk"
    stages: dict
    message: str
    timestamp: str


# ==========================================
# Health Check Schema
# ==========================================

class HealthResponse(BaseModel):
    """System health check response."""
    status: str = "ok"
    service: str = "motor-monitoring-backend"
    timestamp: str
