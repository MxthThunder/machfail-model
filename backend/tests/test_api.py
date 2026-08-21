"""Automated test suite for ESP32 Motor Monitoring Backend API."""

import time
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.services.motor_service import motor_service
from app.models import MotorReading
from app.services.ml_service import ml_service, MLFeaturePayload

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Recreate tables and reset service in-memory state before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    motor_service.latest_readings.clear()
    motor_service.last_seen_times.clear()
    motor_service.last_statuses.clear()
    motor_service.accumulated_runtimes.clear()
    motor_service.pending_commands.clear()
    yield


# ==========================================
# 1. Health Endpoint Test
# ==========================================

def test_health_check():
    """Verify GET /api/health returns 200 OK and valid status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "motor-monitoring-backend"
    assert "timestamp" in data


# ==========================================
# 2. ESP32 Sensor Data Ingestion Test
# ==========================================

def test_ingest_esp32_sensor_data():
    """Verify POST /api/motor/data accepts the exact real ESP32 sensor payload."""
    payload = {
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
        "esp32_ip": "192.168.1.150"
    }
    response = client.post("/api/motor/data", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Motor data received"
    assert data["motor_id"] == "M001"
    assert "timestamp" in data


# ==========================================
# 3. Latest Data Retrieval Test
# ==========================================

def test_get_latest_motor_data():
    """Verify GET /api/motor/latest retrieves the most recent real sensor reading including new fields."""
    # 404 when no data exists
    res_empty = client.get("/api/motor/latest?motor_id=M001")
    assert res_empty.status_code == 404

    # Ingest real payload
    payload = {
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
        "esp32_ip": "192.168.1.150"
    }
    client.post("/api/motor/data", json=payload)

    # Query latest
    response = client.get("/api/motor/latest?motor_id=M001")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "M001"
    assert data["status"] == "ON"
    assert data["temperature"] == 33.9
    assert data["humidity"] == 69.0
    assert data["ir"] == 0
    assert data["ir_pulses"] == 5516
    assert data["rpm"] == 2945.7
    assert data["acs_adc"] == 530
    assert data["current"] == 0.08
    assert data["vibration_level"] == "HIGH"
    assert data["motor_pwm"] == 255
    assert data["esp32_ip"] == "192.168.1.150"
    assert "received_at" in data


# ==========================================
# 4. Motor Status & Runtime Test
# ==========================================

def test_motor_status_and_runtime():
    """Verify GET /api/motor/status returns online state and runtime."""
    # Before data: offline
    res_init = client.get("/api/motor/status?motor_id=M001")
    assert res_init.status_code == 200
    assert res_init.json()["online"] is False

    # Ingest data
    payload = {
        "motor_id": "M001",
        "status": "ON",
        "temperature": 35.0,
        "humidity": 55.0,
        "ir": 1,
        "acs_adc": 1800,
        "current": 1.5,
        "mpu_x": 0.0,
        "mpu_y": 1.0,
        "mpu_z": 0.0,
        "total_acceleration": 1.0,
        "vibration": 0.0,
        "vibration_level": "LOW"
    }
    client.post("/api/motor/data", json=payload)

    # Status should now be online
    res_online = client.get("/api/motor/status?motor_id=M001")
    assert res_online.status_code == 200
    status_data = res_online.json()
    assert status_data["online"] is True
    assert status_data["status"] == "ON"
    assert status_data["last_seen"] is not None


# ==========================================
# 5. History Query Test
# ==========================================

def test_motor_history():
    """Verify GET /api/motor/history/{motor_id} returns historical sensor records."""
    # Ingest 3 records
    for i in range(3):
        payload = {
            "motor_id": "M001",
            "status": "ON",
            "temperature": 40.0 + i,
            "humidity": 50.0,
            "ir": 1,
            "acs_adc": 1800,
            "current": 2.0,
            "mpu_x": 0.1,
            "mpu_y": -0.9,
            "mpu_z": 0.0,
            "total_acceleration": 1.0,
            "vibration": 0.0,
            "vibration_level": "LOW"
        }
        client.post("/api/motor/data", json=payload)

    response = client.get("/api/motor/history/M001?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "M001"
    assert data["count"] == 2
    assert len(data["records"]) == 2
    # Verify latest record is first in reverse chronological order
    assert data["records"][0]["temperature"] == 42.0


# ==========================================
# 6. Invalid Sensor Data Validation Test
# ==========================================

def test_invalid_sensor_data_validation():
    """Verify 422 Unprocessable Entity on missing or ill-typed sensor fields."""
    # Missing required field 'current'
    invalid_payload = {
        "motor_id": "M001",
        "status": "ON",
        "temperature": 40.0,
        "humidity": 50.0,
        "ir": 1,
        "acs_adc": 1800,
        # missing current
        "mpu_x": 0.1,
        "mpu_y": -0.9,
        "mpu_z": 0.0,
        "total_acceleration": 1.0,
        "vibration": 0.0,
        "vibration_level": "LOW"
    }
    response = client.post("/api/motor/data", json=invalid_payload)
    assert response.status_code == 422
    err = response.json()
    assert "detail" in err or "error" in err


# ==========================================
# 7 & 8 & 9. Motor Control & Polling & Ack Test
# ==========================================

def test_motor_control_polling_and_ack():
    """Verify motor control command queueing, ESP32 polling, and execution acknowledgement."""
    # Ingest initial state showing motor is physically OFF
    init_payload = {
        "motor_id": "M001",
        "status": "OFF",
        "temperature": 30.0,
        "humidity": 50.0,
        "ir": 0,
        "acs_adc": 0,
        "current": 0.0,
        "mpu_x": 0.0,
        "mpu_y": 0.0,
        "mpu_z": 1.0,
        "total_acceleration": 1.0,
        "vibration": 0.0,
        "vibration_level": "LOW"
    }
    client.post("/api/motor/data", json=init_payload)

    # 1. User/Dashboard requests motor ON
    ctrl_res = client.post("/api/motor/control", json={"motor_id": "M001", "command": "ON"})
    assert ctrl_res.status_code == 200
    ctrl_data = ctrl_res.json()
    assert ctrl_data["requested_command"] == "ON"
    assert ctrl_data["actual_status"] == "OFF"  # Backend does NOT falsely claim motor is ON yet
    assert ctrl_data["command_status"] == "PENDING"
    command_id = ctrl_data["command_id"]

    # 2. ESP32 polls for pending commands
    poll_res = client.get("/api/motor/command/M001")
    assert poll_res.status_code == 200
    poll_data = poll_res.json()
    assert poll_data["has_pending_command"] is True
    assert poll_data["command"] == "ON"
    assert poll_data["command_id"] == command_id

    # 3. ESP32 acknowledges execution
    ack_res = client.post(
        "/api/motor/command/ack",
        json={"motor_id": "M001", "command_id": command_id, "status": "EXECUTED"}
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["success"] is True

    # 4. Subsequent poll shows no pending commands
    poll_res2 = client.get("/api/motor/command/M001")
    assert poll_res2.status_code == 200
    assert poll_res2.json()["has_pending_command"] is False


# ==========================================
# 10. Online/Offline Timeout Logic Test
# ==========================================

def test_online_offline_timeout_logic():
    """Verify that motor is marked offline when last received data exceeds timeout threshold."""
    # Set simulated last seen timestamp to 30 seconds ago (threshold is 10s)
    past_time = datetime.now(timezone.utc) - timedelta(seconds=30)
    motor_service.last_seen_times["M001"] = past_time
    motor_service.last_statuses["M001"] = "ON"

    res = client.get("/api/motor/status?motor_id=M001")
    assert res.status_code == 200
    data = res.json()
    assert data["online"] is False
    assert data["motor_id"] == "M001"


# ==========================================
# 11. ML Service Interface Boundary Test
# ==========================================

def test_ml_service_boundary():
    """Verify ML service boundary accepts features and does not return fake predictions."""
    payload = MLFeaturePayload(
        motor_id="M001",
        temperature=42.5,
        humidity=62.2,
        current=2.40,
        voltage=None,
        mpu_x=0.259,
        mpu_y=-0.965,
        mpu_z=-0.062,
        total_acceleration=1.021,
        vibration=0.021,
        motor_runtime_seconds=120.0
    )
    # ML model is not yet loaded, so predict_health must return None (no fake values)
    result = ml_service.predict_health(payload)
    assert result is None


# ==========================================
# 12. WebSocket Test
# ==========================================

def test_websocket_realtime_broadcast():
    """Verify WebSocket connection, ping/pong heartbeat, and live ESP32 telemetry broadcast."""
    with client.websocket_connect("/ws/motor/M001") as websocket:
        websocket.send_text("ping")
        response = websocket.receive_text()
        assert response == "pong"

        # Ingest real ESP32 data while WebSocket client is listening
        payload = {
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
            "esp32_ip": "192.168.1.150"
        }
        res = client.post("/api/motor/data", json=payload)
        assert res.status_code == 201

        # Receive real-time push message
        msg = websocket.receive_json()
        assert msg["type"] == "telemetry"
        assert msg["online"] is True
        assert msg["data"]["rpm"] == 2945.7
        assert msg["data"]["ir_pulses"] == 5516
        assert msg["data"]["motor_pwm"] == 255
        assert msg["data"]["temperature"] == 33.9
        assert msg["data"]["vibration_level"] == "HIGH"
