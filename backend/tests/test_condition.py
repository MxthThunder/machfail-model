"""Automated tests for Motor Condition Analysis & Rule-Based Failure Risk."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app.services.motor_service import motor_service
from app.services.condition_service import condition_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database and in-memory caches before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    motor_service.latest_readings.clear()
    motor_service.last_seen_times.clear()
    motor_service.last_statuses.clear()
    motor_service.accumulated_runtimes.clear()
    yield


# ==========================================
# 1. User Specified TEST 1
# ==========================================
def test_condition_case_1_all_normal():
    """
    TEST 1:
    Temperature = 32
    RPM = 1500
    Current = 0.5
    Vibration = 1000
    Expected: All NORMAL, Overall = NORMAL, Score = 0, Risk = LOW
    """
    res = condition_service.evaluate_condition(
        motor_id="M001",
        temperature=32.0,
        rpm=1500.0,
        current=0.5,
        vibration=1000.0
    )
    assert res["temperature"]["condition"] == "NORMAL"
    assert res["temperature"]["score"] == 0
    assert res["rpm"]["condition"] == "NORMAL"
    assert res["rpm"]["score"] == 0
    assert res["current"]["condition"] == "NORMAL"
    assert res["current"]["score"] == 0
    assert res["vibration"]["condition"] == "NORMAL"
    assert res["vibration"]["score"] == 0
    assert res["overall_condition"] == "NORMAL"
    assert res["condition_score"] == 0
    assert res["maximum_score"] == 8
    assert res["failure_risk"] == "LOW"
    assert res["message"] == "Motor operating normally"


# ==========================================
# 2. User Specified TEST 2
# ==========================================
def test_condition_case_2_all_medium():
    """
    TEST 2:
    Temperature = 37
    RPM = 800
    Current = 1.2
    Vibration = 2500
    Expected: All MEDIUM, Overall = MEDIUM, Score = 4, Risk = MEDIUM
    """
    res = condition_service.evaluate_condition(
        motor_id="M001",
        temperature=37.0,
        rpm=800.0,
        current=1.2,
        vibration=2500.0
    )
    assert res["temperature"]["condition"] == "MEDIUM"
    assert res["temperature"]["score"] == 1
    assert res["rpm"]["condition"] == "MEDIUM"
    assert res["rpm"]["score"] == 1
    assert res["current"]["condition"] == "MEDIUM"
    assert res["current"]["score"] == 1
    assert res["vibration"]["condition"] == "MEDIUM"
    assert res["vibration"]["score"] == 1
    assert res["overall_condition"] == "MEDIUM"
    assert res["condition_score"] == 4
    assert res["failure_risk"] == "MEDIUM"


# ==========================================
# 3. User Specified TEST 3
# ==========================================
def test_condition_case_3_all_high():
    """
    TEST 3:
    Temperature = 42
    RPM = 300
    Current = 1.7
    Vibration = 3500
    Expected: All HIGH, Overall = HIGH, Score = 8, Risk = HIGH
    """
    res = condition_service.evaluate_condition(
        motor_id="M001",
        temperature=42.0,
        rpm=300.0,
        current=1.7,
        vibration=3500.0
    )
    assert res["temperature"]["condition"] == "HIGH"
    assert res["temperature"]["score"] == 2
    assert res["rpm"]["condition"] == "HIGH"
    assert res["rpm"]["score"] == 2
    assert res["current"]["condition"] == "HIGH"
    assert res["current"]["score"] == 2
    assert res["vibration"]["condition"] == "HIGH"
    assert res["vibration"]["score"] == 2
    assert res["overall_condition"] == "HIGH"
    assert res["condition_score"] == 8
    assert res["failure_risk"] == "HIGH"


# ==========================================
# 4. User Specified TEST 4
# ==========================================
def test_condition_case_4_real_baseline():
    """
    TEST 4:
    Temperature = 32.9
    RPM = 1340.7
    Current = 0.0
    Vibration = 0.035
    Expected: All NORMAL, Overall = NORMAL, Score = 0, Risk = LOW
    """
    res = condition_service.evaluate_condition(
        motor_id="M001",
        temperature=32.9,
        rpm=1340.7,
        current=0.0,
        vibration=0.035
    )
    assert res["temperature"]["condition"] == "NORMAL"
    assert res["rpm"]["condition"] == "NORMAL"
    assert res["current"]["condition"] == "NORMAL"
    assert res["vibration"]["condition"] == "NORMAL"
    assert res["overall_condition"] == "NORMAL"
    assert res["condition_score"] == 0
    assert res["failure_risk"] == "LOW"
    assert res["message"] == "Motor operating normally"


# ==========================================
# 5. User Specified TEST 5
# ==========================================
def test_condition_case_5_single_medium():
    """
    TEST 5:
    Temperature = 36
    RPM = 1400
    Current = 0.8
    Vibration = 1000
    Expected: Temperature = MEDIUM, Others = NORMAL, Overall = MEDIUM, Score = 1
    """
    res = condition_service.evaluate_condition(
        motor_id="M001",
        temperature=36.0,
        rpm=1400.0,
        current=0.8,
        vibration=1000.0
    )
    assert res["temperature"]["condition"] == "MEDIUM"
    assert res["temperature"]["score"] == 1
    assert res["rpm"]["condition"] == "NORMAL"
    assert res["current"]["condition"] == "NORMAL"
    assert res["vibration"]["condition"] == "NORMAL"
    assert res["overall_condition"] == "MEDIUM"
    assert res["condition_score"] == 1
    assert res["failure_risk"] == "MEDIUM"
    assert "Elevated temperature" in res["message"]


# ==========================================
# 6. Boundary Conditions Tests
# ==========================================
def test_boundary_rules():
    """Verify exact boundary values as specified."""
    # RPM: 1000 is MEDIUM, 1000.1 is NORMAL
    assert condition_service.evaluate_condition("M001", 32, 1000.0, 0.5, 50)["rpm"]["condition"] == "MEDIUM"
    assert condition_service.evaluate_condition("M001", 32, 1001.0, 0.5, 50)["rpm"]["condition"] == "NORMAL"
    assert condition_service.evaluate_condition("M001", 32, 499.0, 0.5, 50)["rpm"]["condition"] == "HIGH"

    # Current: 1.0 is MEDIUM, 1.5 is HIGH
    assert condition_service.evaluate_condition("M001", 32, 1200, 1.0, 50)["current"]["condition"] == "MEDIUM"
    assert condition_service.evaluate_condition("M001", 32, 1200, 0.99, 50)["current"]["condition"] == "NORMAL"
    assert condition_service.evaluate_condition("M001", 32, 1200, 1.5, 50)["current"]["condition"] == "HIGH"

    # Temperature: 35.0 is MEDIUM, 40.0 is HIGH
    assert condition_service.evaluate_condition("M001", 35.0, 1200, 0.5, 50)["temperature"]["condition"] == "MEDIUM"
    assert condition_service.evaluate_condition("M001", 40.0, 1200, 0.5, 50)["temperature"]["condition"] == "HIGH"

    # Vibration: 2000 is NORMAL, 2001 is MEDIUM, 3001 is HIGH
    assert condition_service.evaluate_condition("M001", 32, 1200, 0.5, 2000.0)["vibration"]["condition"] == "NORMAL"
    assert condition_service.evaluate_condition("M001", 32, 1200, 0.5, 2500.0)["vibration"]["condition"] == "MEDIUM"
    assert condition_service.evaluate_condition("M001", 32, 1200, 0.5, 3001.0)["vibration"]["condition"] == "HIGH"


# ==========================================
# 7. POST /api/motor/analyze API Test
# ==========================================
def test_api_motor_analyze():
    """Verify POST /api/motor/analyze endpoint."""
    payload = {
        "motor_id": "M001",
        "temperature": 36.5,
        "rpm": 1200.0,
        "current": 1.6,
        "vibration": 500.0
    }
    res = client.post("/api/motor/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["motor_id"] == "M001"
    assert data["temperature"]["condition"] == "MEDIUM"
    assert data["current"]["condition"] == "HIGH"
    assert data["overall_condition"] == "HIGH"
    assert data["failure_risk"] == "HIGH"
    assert data["risk_type"] == "Rule-Based Failure Risk"
    assert "high motor current" in data["message"].lower()
    assert "elevated temperature" in data["message"].lower()


# ==========================================
# 8. GET /api/motor/condition/{motor_id} Test
# ==========================================
def test_api_motor_condition_from_latest_telemetry():
    """Verify GET /api/motor/condition/M001 analyzes real ingested telemetry."""
    # 404 when no telemetry
    res404 = client.get("/api/motor/condition/M001")
    assert res404.status_code == 404

    # Ingest real ESP32 telemetry
    real_telemetry = {
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
    client.post("/api/motor/data", json=real_telemetry)

    # Fetch condition analysis of latest reading
    res = client.get("/api/motor/condition/M001")
    assert res.status_code == 200
    data = res.json()
    assert data["motor_id"] == "M001"
    assert data["temperature"]["value"] == 33.9
    assert data["temperature"]["condition"] == "NORMAL"
    assert data["rpm"]["value"] == 2945.7
    assert data["rpm"]["condition"] == "NORMAL"
    assert data["current"]["value"] == 0.08
    assert data["current"]["condition"] == "NORMAL"
    assert data["vibration"]["value"] == 0.53
    assert data["vibration"]["condition"] == "NORMAL"
    assert data["overall_condition"] == "NORMAL"
    assert data["condition_score"] == 0
    assert data["failure_risk"] == "LOW"
    assert data["stages"]["sensor_data_analysis"] == "Complete"
    assert data["stages"]["motor_condition_prediction"] == "Complete"
    assert data["stages"]["failure_risk_analysis"] == "Complete"
