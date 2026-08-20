"""Stage 9 FastAPI Endpoints Unit Tests."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api import app

client = TestClient(app)


def test_api_health_endpoint():
    """Verify GET /health returns 200 and status 'ok'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "industrial-ai-prediction-service"


def test_api_model_info_endpoint():
    """Verify GET /model-info returns metadata JSON."""
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "RandomForestClassifier"
    assert "feature_names" in data
    assert "class_mapping" in data


def test_api_predict_valid_payload():
    """Verify POST /predict returns 200 and valid prediction structure."""
    payload = {
        "rpm": 1380.0,
        "temperature": 42.5,
        "humidity": 62.0,
        "current": 0.98,
        "vibration": 0.28,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "WARNING"
    assert data["status_code"] == 1
    assert 70 <= data["health_score"] <= 89
    assert data["confidence"] > 0.5
    assert len(data["contributing_factors"]) >= 1


def test_api_predict_rejects_negative_rpm():
    """Verify Pydantic rejects negative RPM with HTTP 422."""
    payload = {
        "rpm": -50.0,  # Invalid negative
        "temperature": 32.0,
        "humidity": 60.0,
        "current": 0.72,
        "vibration": 0.10,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_api_predict_rejects_extreme_temperature():
    """Verify Pydantic rejects impossible temperatures (> 120 C) with HTTP 422."""
    payload = {
        "rpm": 1500.0,
        "temperature": 180.0,  # Invalid extreme temp
        "humidity": 60.0,
        "current": 0.72,
        "vibration": 0.10,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_api_predict_rejects_missing_fields():
    """Verify Pydantic rejects incomplete payloads with HTTP 422."""
    payload = {
        "rpm": 1500.0,
        "temperature": 32.0,
        # Missing 'humidity', 'current', 'vibration'
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


if __name__ == "__main__":
    test_api_health_endpoint()
    test_api_model_info_endpoint()
    test_api_predict_valid_payload()
    test_api_predict_rejects_negative_rpm()
    test_api_predict_rejects_extreme_temperature()
    test_api_predict_rejects_missing_fields()
    print("All Stage 9 API tests passed successfully!")
