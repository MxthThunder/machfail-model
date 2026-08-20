"""Stage 9 Predictor Unit Tests."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SENSOR_FEATURES
from src.predictor import MachinePredictor, predict_machine_status


def test_predictor_normal_telemetry():
    """Verify inference for nominal normal telemetry."""
    res = predict_machine_status(
        rpm=1510.0,
        temperature=32.0,
        humidity=58.0,
        current=0.72,
        vibration=0.095,
    )
    assert res["status"] == "NORMAL"
    assert res["status_code"] == 0
    assert res["health_score"] >= 90
    assert res["confidence"] >= 0.70
    assert "Nominal operating conditions" in res["prediction"]


def test_predictor_warning_telemetry():
    """Verify inference for elevated warning telemetry."""
    res = predict_machine_status(
        rpm=1380.0,
        temperature=43.0,
        humidity=61.0,
        current=0.98,
        vibration=0.28,
    )
    assert res["status"] == "WARNING"
    assert res["status_code"] == 1
    assert 70 <= res["health_score"] <= 89
    assert "consistent with possible motor overload" in res["prediction"]


def test_predictor_fault_telemetry():
    """Verify inference for severe fault telemetry."""
    res = predict_machine_status(
        rpm=920.0,
        temperature=58.0,
        humidity=65.0,
        current=1.60,
        vibration=0.65,
    )
    assert res["status"] == "FAULT"
    assert res["status_code"] == 2
    assert res["health_score"] <= 69
    assert "Critical sensor pattern" in res["prediction"]


def test_predictor_schema_and_probabilities():
    """Verify predictor output schema and probability constraints."""
    res = predict_machine_status(
        rpm=1500.0,
        temperature=32.0,
        humidity=60.0,
        current=0.72,
        vibration=0.10,
    )
    expected_keys = [
        "status",
        "status_code",
        "health_score",
        "health_category",
        "confidence",
        "prediction",
        "probabilities",
        "contributing_factors",
        "timestamp",
        "model_version",
    ]
    for k in expected_keys:
        assert k in res, f"Key '{k}' missing from predictor output"

    probs = res["probabilities"]
    assert set(probs.keys()) == {"NORMAL", "WARNING", "FAULT"}
    assert abs(sum(probs.values()) - 1.0) < 1e-3


if __name__ == "__main__":
    test_predictor_normal_telemetry()
    test_predictor_warning_telemetry()
    test_predictor_fault_telemetry()
    test_predictor_schema_and_probabilities()
    print("All Stage 9 predictor tests passed successfully!")
