"""Automated tests verifying Simulation Mode vs Live Mode isolation and unified condition analysis."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import MotorReading, MotorCommand
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


def test_simulation_does_not_modify_database_or_hardware():
    """Verify that simulating condition analysis does not insert records or modify state."""
    db = SessionLocal()
    initial_count = db.query(MotorReading).count()
    initial_cmds = db.query(MotorCommand).count()
    db.close()

    sim_payload = {
        "motor_id": "M001-SIMULATED",
        "temperature": 42.5,
        "rpm": 450.0,
        "current": 1.8,
        "vibration": 3500.0
    }
    response = client.post("/api/motor/analyze", json=sim_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_condition"] == "HIGH"
    assert data["failure_risk"] == "HIGH"
    assert data["condition_score"] == 8

    # Check database was untouched
    db = SessionLocal()
    assert db.query(MotorReading).count() == initial_count
    assert db.query(MotorCommand).count() == initial_cmds
    db.close()


def test_simulation_and_live_use_same_classification_logic():
    """Verify that both live hardware telemetry and simulated manual inputs yield identical results."""
    # 1. Simulate manually
    sim_res = condition_service.evaluate_condition(
        motor_id="M001-SIM",
        temperature=37.0,
        rpm=800.0,
        current=1.2,
        vibration=2500.0
    )

    # 2. Ingest via live telemetry API
    live_payload = {
        "motor_id": "M001",
        "status": "ON",
        "temperature": 37.0,
        "humidity": 65.0,
        "ir": 0,
        "ir_pulses": 200,
        "rpm": 800.0,
        "acs_adc": 600,
        "current": 1.2,
        "mpu_x": 0.0,
        "mpu_y": 0.0,
        "mpu_z": 1.0,
        "total_acceleration": 1.0,
        "vibration": 2500.0,
        "vibration_level": "MEDIUM",
        "motor_pwm": 200,
        "voltage": None,
        "esp32_ip": "192.168.1.50"
    }
    client.post("/api/motor/data", json=live_payload)

    # 3. Fetch live condition analysis
    live_res = client.get("/api/motor/condition/M001").json()

    # Assert matching evaluations
    assert sim_res["temperature"]["condition"] == live_res["temperature"]["condition"] == "MEDIUM"
    assert sim_res["rpm"]["condition"] == live_res["rpm"]["condition"] == "MEDIUM"
    assert sim_res["current"]["condition"] == live_res["current"]["condition"] == "MEDIUM"
    assert sim_res["vibration"]["condition"] == live_res["vibration"]["condition"] == "MEDIUM"
    assert sim_res["overall_condition"] == live_res["overall_condition"] == "MEDIUM"
    assert sim_res["condition_score"] == live_res["condition_score"] == 4
    assert sim_res["failure_risk"] == live_res["failure_risk"] == "MEDIUM"
    assert sim_res["risk_type"] == live_res["risk_type"] == "Rule-Based Failure Risk"
