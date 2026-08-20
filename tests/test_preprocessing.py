"""Stage 5 Preprocessing and Scaling Unit Tests."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SCALER_FILE,
    SENSOR_FEATURES,
    TARGET_COLUMN,
)
from src.data_loader import load_and_validate
from src.preprocessing import (
    prepare_features_and_target,
    split_data,
    fit_and_save_scaler,
    load_scaler,
    scale_features,
    run_preprocessing_pipeline,
)


def test_prepare_features_and_target():
    """Verify feature matrix X and target y extraction."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    df, report = load_and_validate(csv_path)
    assert report.is_valid is True

    X, y = prepare_features_and_target(df)
    assert list(X.columns) == SENSOR_FEATURES
    assert len(X) == len(df)
    assert len(y) == len(df)
    assert y.name == TARGET_COLUMN


def test_stratified_split_proportions():
    """Verify 80/20 train/test split and class ratio preservation."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    df, _ = load_and_validate(csv_path)
    X, y = prepare_features_and_target(df)

    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

    # Check split sizes (80% / 20%)
    assert len(X_train) == int(len(df) * 0.8)
    assert len(X_test) == int(len(df) * 0.2)

    # Check stratified class ratios match closely between train and test
    train_proportions = y_train.value_counts(normalize=True).sort_index()
    test_proportions = y_test.value_counts(normalize=True).sort_index()

    for status_code in [0, 1, 2]:
        train_p = train_proportions.get(status_code, 0.0)
        test_p = test_proportions.get(status_code, 0.0)
        assert abs(train_p - test_p) < 0.02, (
            f"Class {status_code} proportion mismatch: train={train_p:.3f}, test={test_p:.3f}"
        )


def test_scaler_leakage_prevention_and_scaling():
    """Verify scaler is fit exclusively on train data and performs correct standardization."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    df, _ = load_and_validate(csv_path)
    X, y = prepare_features_and_target(df)
    X_train, X_test, _, _ = split_data(X, y, test_size=0.2, random_state=42)

    scaler = fit_and_save_scaler(X_train, scaler_path=SCALER_FILE)
    loaded_scaler = load_scaler(SCALER_FILE)

    # Check scaler means match training data means exactly
    for idx, feature in enumerate(SENSOR_FEATURES):
        expected_mean = float(X_train[feature].mean())
        assert abs(scaler.mean_[idx] - expected_mean) < 1e-4
        assert abs(loaded_scaler.mean_[idx] - expected_mean) < 1e-4

    # Check transform output
    X_train_scaled = scale_features(X_train, scaler)
    assert list(X_train_scaled.columns) == SENSOR_FEATURES
    assert len(X_train_scaled) == len(X_train)

    # Train scaled means should be close to 0 and std close to 1
    for feature in SENSOR_FEATURES:
        assert abs(X_train_scaled[feature].mean()) < 1e-2
        assert abs(X_train_scaled[feature].std(ddof=0) - 1.0) < 1e-2


def test_preprocessing_pipeline_export():
    """Verify full pipeline creates train.csv, test.csv and scaler.joblib."""
    summary = run_preprocessing_pipeline()

    train_file = PROCESSED_DATA_DIR / "train.csv"
    test_file = PROCESSED_DATA_DIR / "test.csv"

    assert train_file.exists()
    assert test_file.exists()
    assert SCALER_FILE.exists()

    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)

    assert len(train_df) + len(test_df) == summary["total_samples"]
    assert TARGET_COLUMN in train_df.columns
    assert TARGET_COLUMN in test_df.columns


if __name__ == "__main__":
    test_prepare_features_and_target()
    test_stratified_split_proportions()
    test_scaler_leakage_prevention_and_scaling()
    test_preprocessing_pipeline_export()
    print("All Stage 5 preprocessing tests passed successfully!")
