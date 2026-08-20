"""FastAPI Microservice for Industrial Machine Health & Predictive Maintenance.

Provides RESTful endpoints for real-time inference (/predict), health checks (/health),
and model provenance introspection (/model-info).
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SENSOR_RANGES, API_HOST, API_PORT
from src.predictor import MachinePredictor, predict_machine_status
from src.train import load_metadata


# Define Pydantic Schemas for Strict Input & Output Validation
class SensorReading(BaseModel):
    """Input telemetry payload schema sent by ESP32 or Dashboard."""

    rpm: float = Field(
        ...,
        ge=SENSOR_RANGES["rpm"]["min"],
        le=SENSOR_RANGES["rpm"]["max"],
        description="Motor rotational speed in RPM (0 to 3000)",
        examples=[1380.0],
    )
    temperature: float = Field(
        ...,
        ge=SENSOR_RANGES["temperature"]["min"],
        le=SENSOR_RANGES["temperature"]["max"],
        description="Motor surface / ambient temperature in deg C (-10 to 120)",
        examples=[42.5],
    )
    humidity: float = Field(
        ...,
        ge=SENSOR_RANGES["humidity"]["min"],
        le=SENSOR_RANGES["humidity"]["max"],
        description="Relative ambient humidity percentage (0 to 100)",
        examples=[62.0],
    )
    current: float = Field(
        ...,
        ge=SENSOR_RANGES["current"]["min"],
        le=SENSOR_RANGES["current"]["max"],
        description="Motor electrical current draw in Amperes (0 to 10)",
        examples=[0.98],
    )
    vibration: float = Field(
        ...,
        ge=SENSOR_RANGES["vibration"]["min"],
        le=SENSOR_RANGES["vibration"]["max"],
        description="Mechanical vibration intensity in g (0 to 5)",
        examples=[0.28],
    )


class PredictionResponse(BaseModel):
    """Output prediction and diagnostic payload returned to caller."""

    status: str = Field(..., description="Condition class: NORMAL, WARNING, or FAULT")
    status_code: int = Field(..., description="0 = NORMAL, 1 = WARNING, 2 = FAULT")
    health_score: int = Field(..., ge=0, le=100, description="AI-derived machine health score (0 - 100)")
    health_category: str = Field(..., description="NORMAL, WARNING, or FAULT")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model prediction probability confidence")
    prediction: str = Field(..., description="Uncertainty-aware diagnostic summary")
    probabilities: Dict[str, float] = Field(..., description="Individual class probabilities")
    contributing_factors: List[str] = Field(..., description="List of physical sensor contributing factors")
    timestamp: str = Field(..., description="Inference execution timestamp in ISO-8601 format")
    model_version: str = Field(..., description="Active ML model version")


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str = "ok"
    service: str = "industrial-ai-prediction-service"
    version: str = "1.0.0"


# Initialize FastAPI Application
app = FastAPI(
    title="Industrial Machine Health & Predictive Maintenance API",
    description=(
        "REST API serving real-time machine condition classification, explainable health scores, "
        "and diagnostic factor analysis for an ESP32-monitored DC motor setup."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Web Dashboard Integration (Person 2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for student development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    tags=["System"],
)
def get_health() -> HealthResponse:
    """Liveness probe endpoint returning operational health status."""
    return HealthResponse()


@app.get(
    "/model-info",
    summary="Model Metadata & Provenance",
    tags=["Model Info"],
)
def get_model_info() -> Dict[str, Any]:
    """Returns training metadata, hyperparameters, feature names, and evaluation metrics."""
    try:
        return load_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model metadata: {str(e)}",
        )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Machine Condition & Health Score",
    tags=["Inference"],
)
def predict(reading: SensorReading) -> PredictionResponse:
    """Accepts real-time sensor measurements, executes ML inference,

    and returns classification, health score, and diagnostic explanation.
    """
    try:
        predictor = MachinePredictor.get_instance()
        result = predictor.predict(
            rpm=reading.rpm,
            temperature=reading.temperature,
            humidity=reading.humidity,
            current=reading.current,
            vibration=reading.vibration,
        )
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    print(f"Starting Industrial AI Prediction API on http://{API_HOST}:{API_PORT}...")
    print(f"Interactive Swagger Docs available at http://127.0.0.1:{API_PORT}/docs")
    uvicorn.run("src.api:app", host=API_HOST, port=API_PORT, reload=True)
