"""Stage 10 ESP32 Hardware Integration Unit Tests."""

import time
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api import app
from scripts.simulate_esp32_stream import get_demo_telemetry_sequence

client = TestClient(app)


def test_esp32_telemetry_stream_sequence():
    """Verify that a sequence of simulated ESP32 readings is processed accurately."""
    sequence = get_demo_telemetry_sequence(count=10)
    assert len(sequence) == 10

    statuses_received = []

    for reading in sequence:
        start_t = time.perf_counter()
        resp = client.post("/predict", json=reading)
        duration_ms = (time.perf_counter() - start_t) * 1000.0

        assert resp.status_code == 200, f"Failed with status: {resp.status_code}"
        data = resp.json()

        # Check required fields
        assert "status" in data
        assert "health_score" in data
        assert "confidence" in data
        assert "prediction" in data
        assert "contributing_factors" in data

        # Check inference latency is well within real-time threshold (< 50ms)
        assert duration_ms < 50.0, f"Inference took too long: {duration_ms:.2f}ms"

        statuses_received.append(data["status"])

    # Verify that sequence experienced state transitions
    assert "NORMAL" in statuses_received
    assert "WARNING" in statuses_received
    assert "FAULT" in statuses_received


def test_esp32_payload_boundary_values():
    """Verify ESP32 boundary sensor transmissions are handled properly."""
    nominal_payload = {
        "rpm": 1490.0,
        "temperature": 32.5,
        "humidity": 61.0,
        "current": 0.82,
        "vibration": 0.18,
    }
    resp = client.post("/predict", json=nominal_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["NORMAL", "WARNING"]
    assert data["health_score"] >= 70


if __name__ == "__main__":
    test_esp32_telemetry_stream_sequence()
    test_esp32_payload_boundary_values()
    print("All Stage 10 ESP32 integration tests passed successfully!")
