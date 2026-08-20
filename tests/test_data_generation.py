"""Stage 2 Synthetic Data Generation Unit Tests."""

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_sample_data import generate_synthetic_dataset, save_sample_json_payloads
from src.config import SENSOR_FEATURES, TARGET_COLUMN, SAMPLE_DATA_DIR


def test_generate_synthetic_dataset_shape():
    """Verify synthetic dataset produces the requested number of rows and columns."""
    n_samples = 150
    df = generate_synthetic_dataset(n_samples=n_samples, random_seed=42)
    assert len(df) == n_samples, f"Expected {n_samples} rows, got {len(df)}"

    expected_cols = ["timestamp"] + SENSOR_FEATURES + [TARGET_COLUMN, "data_source"]
    assert list(df.columns) == expected_cols, f"Columns must match standard schema: {expected_cols}"


def test_synthetic_data_integrity():
    """Verify data types and value sanity."""
    df = generate_synthetic_dataset(n_samples=100, random_seed=42)

    # Check status values
    unique_statuses = set(df["status"].unique())
    assert unique_statuses.issubset({0, 1, 2}), f"Statuses must only be 0, 1, 2; got {unique_statuses}"

    # Check data_source tag
    assert (df["data_source"] == "synthetic").all(), "All rows must be explicitly tagged as 'synthetic'"

    # Check non-negativity
    for col in SENSOR_FEATURES:
        assert (df[col] >= 0).all(), f"Sensor feature '{col}' should not have negative values in valid generator output"


def test_sample_json_payloads():
    """Verify sample JSON payloads are created and contain all required sensor keys."""
    save_sample_json_payloads()
    for filename in ["normal_reading.json", "warning_reading.json", "fault_reading.json"]:
        filepath = SAMPLE_DATA_DIR / filename
        assert filepath.exists(), f"Sample payload {filename} must exist"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for feature in SENSOR_FEATURES:
            assert feature in data, f"Key '{feature}' missing from {filename}"


if __name__ == "__main__":
    test_generate_synthetic_dataset_shape()
    test_synthetic_data_integrity()
    test_sample_json_payloads()
    print("All Stage 2 data generation tests passed successfully!")
