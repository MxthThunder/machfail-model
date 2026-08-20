"""Stage 11 Feature Engineering Unit Tests."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_DIR, SENSOR_FEATURES
from src.feature_engineering import (
    ENGINEERED_FEATURE_NAMES,
    ALL_FEATURES_WITH_ENGINEERED,
    create_temporal_features,
    compare_feature_sets,
)


def test_create_temporal_features_columns_and_nans():
    """Verify engineered columns exist and contain zero NaNs."""
    raw_data = {
        "timestamp": [f"2026-08-20T10:0{i}:00" for i in range(10)],
        "rpm": [1500.0, 1495.0, 1480.0, 1450.0, 1400.0, 1350.0, 1300.0, 1200.0, 1100.0, 1000.0],
        "temperature": [32.0, 32.5, 33.0, 34.2, 36.0, 38.5, 42.0, 47.0, 52.0, 58.0],
        "humidity": [60.0] * 10,
        "current": [0.70, 0.71, 0.73, 0.80, 0.90, 1.05, 1.20, 1.40, 1.55, 1.70],
        "vibration": [0.10, 0.11, 0.12, 0.15, 0.22, 0.30, 0.40, 0.52, 0.65, 0.80],
        "status": [0, 0, 0, 1, 1, 1, 1, 2, 2, 2],
    }
    df = pd.DataFrame(raw_data)
    df_feat = create_temporal_features(df, window_size=3)

    for col in ENGINEERED_FEATURE_NAMES:
        assert col in df_feat.columns, f"Engineered feature {col} missing from output"
        assert df_feat[col].isna().sum() == 0, f"Engineered feature {col} contains NaNs"

    assert len(df_feat) == 10


def test_temporal_causality():
    """Verify first-order diff and rolling values match expected backward-looking formulas."""
    df = pd.DataFrame(
        {
            "rpm": [1500.0, 1450.0, 1400.0],
            "temperature": [30.0, 35.0, 40.0],
            "humidity": [60.0, 60.0, 60.0],
            "current": [1.0, 1.2, 1.4],
            "vibration": [0.1, 0.2, 0.3],
        }
    )
    df_feat = create_temporal_features(df, window_size=2)

    # First row diff should be 0.0 (fillna)
    assert df_feat.loc[0, "rpm_change"] == 0.0
    # Second row diff: 1450 - 1500 = -50.0
    assert df_feat.loc[1, "rpm_change"] == -50.0
    # Temperature rate: 35.0 - 30.0 = 5.0
    assert df_feat.loc[1, "temperature_rate"] == 5.0
    # Rolling temp at index 1 with window 2: (30 + 35)/2 = 32.5
    assert df_feat.loc[1, "rolling_temperature"] == 32.5


def test_compare_feature_sets_execution():
    """Verify compare_feature_sets executes and returns valid metrics."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    assert csv_path.exists()

    res = compare_feature_sets(csv_path, n_splits=3)
    assert "baseline_features" in res
    assert "enhanced_features" in res
    assert "feature_importances" in res
    assert res["enhanced_features"]["feature_count"] == len(ALL_FEATURES_WITH_ENGINEERED)


if __name__ == "__main__":
    test_create_temporal_features_columns_and_nans()
    test_temporal_causality()
    test_compare_feature_sets_execution()
    print("All Stage 11 feature engineering tests passed successfully!")
