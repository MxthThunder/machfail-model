"""Data Preprocessing Module for Industrial Machine AI Subsystem.

Handles feature-target separation, stratified splitting, leakage-free feature scaling,
and saving artifacts (train/test datasets and scaler.joblib).
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple, Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    SCALER_FILE,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
    RANDOM_SEED,
)
from src.data_loader import load_and_validate


def prepare_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Extracts the feature matrix X and target vector y from a validated telemetry DataFrame."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing from dataframe.")

    for col in SENSOR_FEATURES:
        if col not in df.columns:
            raise ValueError(f"Required sensor feature '{col}' missing from dataframe.")

    X = df[SENSOR_FEATURES].copy()
    y = df[TARGET_COLUMN].astype(int).copy()
    return X, y


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = RANDOM_SEED,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Splits dataset into stratified train and test sets to maintain class proportions.

    Stratification ensures that rare classes (e.g. FAULT) are evenly represented
    in both training and test partitions.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test


def fit_and_save_scaler(
    X_train: pd.DataFrame,
    scaler_path: Path = SCALER_FILE,
) -> StandardScaler:
    """Fits a StandardScaler strictly on the training set and saves it to disk.

    Fitting strictly on training data prevents 'Data Leakage' from the test set.
    """
    scaler_path.parent.mkdir(parents=True, exist_ok=True)

    scaler = StandardScaler()
    scaler.fit(X_train[SENSOR_FEATURES])

    joblib.dump(scaler, scaler_path)
    return scaler


def load_scaler(scaler_path: Path = SCALER_FILE) -> StandardScaler:
    """Loads a pre-fitted StandardScaler from disk."""
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler file not found at: {scaler_path}")
    return joblib.load(scaler_path)


def scale_features(X: pd.DataFrame, scaler: StandardScaler) -> pd.DataFrame:
    """Transforms feature matrix using a pre-fitted StandardScaler, preserving column names."""
    scaled_array = scaler.transform(X[SENSOR_FEATURES])
    scaled_df = pd.DataFrame(scaled_array, columns=SENSOR_FEATURES, index=X.index)
    return scaled_df


def run_preprocessing_pipeline(
    input_csv: Path | str = RAW_DATA_DIR / "synthetic_machine_data.csv",
    output_dir: Path | str = PROCESSED_DATA_DIR,
    scaler_path: Path | str = SCALER_FILE,
    test_size: float = 0.2,
    random_state: int = RANDOM_SEED,
) -> Dict[str, Any]:
    """Executes the complete end-to-end preprocessing workflow:

    1. Load and validate raw dataset.
    2. Extract standard sensor features X and target status y.
    3. Stratified 80/20 train/test split.
    4. Fit StandardScaler on X_train only and save scaler.joblib.
    5. Save processed train.csv and test.csv into data/processed/.
    """
    input_path = Path(input_csv)
    out_dir = Path(output_dir)
    out_scaler = Path(scaler_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_scaler.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load and validate
    df, report = load_and_validate(input_path)
    if not report.is_valid:
        print("[WARNING] Issues detected during validation, using cleaned records only.")

    # 2. Extract features and target
    X, y = prepare_features_and_target(df)

    # 3. Stratified Split
    X_train, X_test, y_train, y_test = split_data(
        X, y, test_size=test_size, random_state=random_state
    )

    # 4. Fit & Save Scaler (leakage-free)
    scaler = fit_and_save_scaler(X_train, scaler_path=out_scaler)

    # 5. Export processed train/test datasets (unscaled for tree models, with helper for scaled)
    train_df = X_train.copy()
    train_df[TARGET_COLUMN] = y_train

    test_df = X_test.copy()
    test_df[TARGET_COLUMN] = y_test

    train_csv = out_dir / "train.csv"
    test_csv = out_dir / "test.csv"

    train_df.to_csv(train_csv, index=False)
    test_df.to_csv(test_csv, index=False)

    return {
        "total_samples": len(df),
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "train_csv": train_csv,
        "test_csv": test_csv,
        "scaler_path": out_scaler,
        "scaler_means": dict(zip(SENSOR_FEATURES, [round(float(m), 3) for m in scaler.mean_])),
        "scaler_stds": dict(zip(SENSOR_FEATURES, [round(float(s), 3) for s in scaler.scale_])),
    }


def main():
    parser = argparse.ArgumentParser(description="Run preprocessing pipeline for machine telemetry.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(RAW_DATA_DIR / "synthetic_machine_data.csv"),
        help="Input raw CSV path",
    )
    args = parser.parse_args()

    print("Running Data Preprocessing Pipeline...")
    summary = run_preprocessing_pipeline(input_csv=args.input)

    print("\n[OK] Preprocessing completed successfully!")
    print("=" * 60)
    print(f"Total Records Processed : {summary['total_samples']}")
    print(f"Training Set (80%)      : {summary['train_samples']} rows -> {summary['train_csv']}")
    print(f"Testing Set  (20%)      : {summary['test_samples']} rows -> {summary['test_csv']}")
    print(f"Fitted Scaler Saved     : {summary['scaler_path']}")
    print("\nFitted Training Feature Means (StandardScaler):")
    for feat, mean_val in summary["scaler_means"].items():
        print(f"  - {feat:12s}: mean = {mean_val:8.3f}, std = {summary['scaler_stds'][feat]:8.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
