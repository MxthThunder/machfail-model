"""Stage 1 Environment and Setup Verification Test."""

import sys
from pathlib import Path

# Add project root to sys.path if not present
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLE_DATA_DIR,
    MODELS_DIR,
    SENSOR_FEATURES,
    STATUS_MAP,
)


def test_project_structure():
    """Verify that all core directories are configured properly."""
    assert PROJECT_ROOT.exists(), "PROJECT_ROOT must exist"
    assert DATA_DIR.exists(), "data/ directory must exist"
    assert RAW_DATA_DIR.exists(), "data/raw/ directory must exist"
    assert PROCESSED_DATA_DIR.exists(), "data/processed/ directory must exist"
    assert SAMPLE_DATA_DIR.exists(), "data/sample/ directory must exist"
    assert MODELS_DIR.exists(), "models/ directory must exist"


def test_sensor_features_config():
    """Verify the 5 standard sensor feature names."""
    expected_features = ["rpm", "temperature", "humidity", "current", "vibration"]
    assert SENSOR_FEATURES == expected_features, f"Features must be {expected_features}"


def test_status_mapping():
    """Verify the 3 standard condition classes."""
    assert STATUS_MAP[0] == "NORMAL"
    assert STATUS_MAP[1] == "WARNING"
    assert STATUS_MAP[2] == "FAULT"


if __name__ == "__main__":
    test_project_structure()
    test_sensor_features_config()
    test_status_mapping()
    print("All Stage 1 setup tests passed successfully!")
