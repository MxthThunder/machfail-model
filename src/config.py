"""Central configuration module for the Industrial Machine AI Subsystem.

This module defines directory paths, sensor feature names, status class mappings,
and default hyperparameters to ensure consistency across the entire project.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
PLOTS_DIR = PROCESSED_DATA_DIR / "plots"

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODELS_DIR / "model.joblib"
SCALER_FILE = MODELS_DIR / "scaler.joblib"
METADATA_FILE = MODELS_DIR / "metadata.json"

# Standard Sensor Features (strictly ordered and named)
SENSOR_FEATURES = [
    "rpm",
    "temperature",
    "humidity",
    "current",
    "vibration",
]

TARGET_COLUMN = "status"

# Class Mapping: 0 = NORMAL, 1 = WARNING, 2 = FAULT
STATUS_MAP = {
    0: "NORMAL",
    1: "WARNING",
    2: "FAULT",
}

STATUS_NAMES = list(STATUS_MAP.values())

# Physical Sensor Boundaries (for input validation and sanity checks)
# These represent feasible physical ranges for the small industrial motor setup.
SENSOR_RANGES = {
    "rpm": {"min": 0.0, "max": 3000.0, "unit": "RPM"},
    "temperature": {"min": -10.0, "max": 120.0, "unit": "°C"},
    "humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
    "current": {"min": 0.0, "max": 10.0, "unit": "A"},
    "vibration": {"min": 0.0, "max": 5.0, "unit": "g / arbitrary unit"},
}

# Machine Health Score Thresholds (0 - 100)
HEALTH_SCORE_THRESHOLDS = {
    "NORMAL": (90, 100),
    "WARNING": (70, 89),
    "FAULT": (0, 69),
}

# Reproducibility
RANDOM_SEED = 42

# API Server Defaults
API_HOST = "0.0.0.0"
API_PORT = 8000
