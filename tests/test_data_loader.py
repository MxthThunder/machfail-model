import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_DIR, SENSOR_FEATURES
from src.data_loader import (
    load_raw_csv,
    validate_dataframe,
    load_and_validate,
    ValidationReport,
)


def test_validate_clean_synthetic_dataset():
    """Verify that our generated synthetic dataset passes all validation checks."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    assert csv_path.exists(), "Synthetic dataset file must exist for testing"

    clean_df, report = load_and_validate(csv_path)
    assert report.is_valid is True
    assert report.total_records == len(clean_df)
    assert report.invalid_records == 0
    assert len(report.errors) == 0


def test_missing_values_detection():
    """Verify that missing values (NaN) are caught and reported."""
    sample_data = {
        "timestamp": ["2026-08-20T10:00:00", "2026-08-20T10:01:00"],
        "rpm": [1500.0, np.nan],  # 1 missing value
        "temperature": [np.nan, 32.5],  # 1 missing value
        "humidity": [60.0, 60.0],
        "current": [0.72, 0.73],
        "vibration": [0.10, 0.11],
        "status": [0, 0],
    }
    df = pd.DataFrame(sample_data)
    clean_df, report = validate_dataframe(df)

    assert report.is_valid is False
    assert any("missing (NaN)" in err for err in report.errors)
    assert len(clean_df) == 0  # Both rows had at least one missing feature


def test_out_of_bounds_detection():
    """Verify out-of-bounds / impossible sensor values are caught."""
    sample_data = {
        "timestamp": ["2026-08-20T10:00:00", "2026-08-20T10:01:00", "2026-08-20T10:02:00"],
        "rpm": [-100.0, 1500.0, 1490.0],  # Negative RPM
        "temperature": [32.0, 185.0, 33.0],  # Extreme Temp > 120 C
        "humidity": [60.0, 60.0, 60.0],
        "current": [0.72, 0.73, 25.0],  # Current > 10 A
        "vibration": [0.10, 0.11, 0.12],
        "status": [0, 0, 0],
    }
    df = pd.DataFrame(sample_data)
    clean_df, report = validate_dataframe(df)

    assert report.is_valid is False
    assert report.invalid_records == 3
    assert any("below physical limit" in err for err in report.errors)
    assert any("exceeding physical limit" in err for err in report.errors)


def test_invalid_status_label_detection():
    """Verify unexpected target class values are flagged."""
    sample_data = {
        "timestamp": ["2026-08-20T10:00:00"],
        "rpm": [1500.0],
        "temperature": [32.0],
        "humidity": [60.0],
        "current": [0.72],
        "vibration": [0.10],
        "status": [99],  # Invalid class label (only 0, 1, 2 allowed)
    }
    df = pd.DataFrame(sample_data)
    clean_df, report = validate_dataframe(df)

    assert report.is_valid is False
    assert any("invalid label" in err for err in report.errors)


def test_missing_required_columns():
    """Verify missing required sensor columns are flagged immediately."""
    sample_data = {
        "timestamp": ["2026-08-20T10:00:00"],
        "rpm": [1500.0],
        "temperature": [32.0],
        # 'humidity', 'current', 'vibration' missing!
    }
    df = pd.DataFrame(sample_data)
    clean_df, report = validate_dataframe(df)

    assert report.is_valid is False
    assert any("Missing required sensor columns" in err for err in report.errors)


def test_nonexistent_file_raises_error():
    """Verify FileNotFoundError on missing files."""
    try:
        load_raw_csv("data/raw/nonexistent_file.csv")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    test_validate_clean_synthetic_dataset()
    test_missing_values_detection()
    test_out_of_bounds_detection()
    test_invalid_status_label_detection()
    test_missing_required_columns()
    test_nonexistent_file_raises_error()
    print("All Stage 3 data loader & validation tests passed successfully!")
