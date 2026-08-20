"""Feature Engineering Module for Industrial Machine Telemetry.

Computes physical derived features (rates of change, differences, and rolling aggregates)
using strictly backward-looking time windows to prevent temporal data leakage.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
    RANDOM_SEED,
)
from src.data_loader import load_and_validate

# Engineered Feature Column Names
ENGINEERED_FEATURE_NAMES = [
    "rpm_change",
    "temperature_rate",
    "current_change",
    "vibration_change",
    "rolling_temperature",
    "rolling_current",
    "rolling_vibration",
]

ALL_FEATURES_WITH_ENGINEERED = SENSOR_FEATURES + ENGINEERED_FEATURE_NAMES


def create_temporal_features(
    df: pd.DataFrame,
    window_size: int = 5,
) -> pd.DataFrame:
    """Derives temporal rate-of-change and rolling average features from sequential telemetry.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame sorted chronologically.
    window_size : int
        Number of previous time steps to include in rolling smoothing (default: 5).

    Returns
    -------
    pd.DataFrame
        DataFrame augmented with engineered physical features.
    """
    df_feat = df.copy()

    # 1. First-Order Differences (Rates of Change: t - (t-1))
    df_feat["rpm_change"] = df_feat["rpm"].diff().fillna(0.0)
    df_feat["temperature_rate"] = df_feat["temperature"].diff().fillna(0.0)
    df_feat["current_change"] = df_feat["current"].diff().fillna(0.0)
    df_feat["vibration_change"] = df_feat["vibration"].diff().fillna(0.0)

    # 2. Backward-Looking Rolling Averages (Dampens instantaneous high-frequency sensor noise)
    df_feat["rolling_temperature"] = (
        df_feat["temperature"].rolling(window=window_size, min_periods=1).mean()
    )
    df_feat["rolling_current"] = (
        df_feat["current"].rolling(window=window_size, min_periods=1).mean()
    )
    df_feat["rolling_vibration"] = (
        df_feat["vibration"].rolling(window=window_size, min_periods=1).mean()
    )

    return df_feat


def compare_feature_sets(
    input_csv: Path | str = RAW_DATA_DIR / "synthetic_machine_data.csv",
    n_splits: int = 5,
) -> Dict[str, Any]:
    """Compares ML model performance before and after temporal feature engineering."""
    df, report = load_and_validate(input_csv)
    df_eng = create_temporal_features(df)

    y = df_eng[TARGET_COLUMN].astype(int)
    X_base = df_eng[SENSOR_FEATURES]
    X_enhanced = df_eng[ALL_FEATURES_WITH_ENGINEERED]

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)

    model_base = RandomForestClassifier(
        n_estimators=100, max_depth=6, class_weight="balanced", random_state=RANDOM_SEED
    )
    model_enhanced = RandomForestClassifier(
        n_estimators=100, max_depth=6, class_weight="balanced", random_state=RANDOM_SEED
    )

    scoring = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]

    cv_base = cross_validate(model_base, X_base, y, cv=skf, scoring=scoring, n_jobs=-1)
    cv_enhanced = cross_validate(model_enhanced, X_enhanced, y, cv=skf, scoring=scoring, n_jobs=-1)

    # Fit enhanced model to extract all feature importances
    model_enhanced.fit(X_enhanced, y)
    importances = {
        feat: round(float(imp) * 100, 2)
        for feat, imp in sorted(
            zip(ALL_FEATURES_WITH_ENGINEERED, model_enhanced.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )
    }

    return {
        "baseline_features": {
            "feature_count": len(SENSOR_FEATURES),
            "cv_accuracy": round(float(np.mean(cv_base["test_accuracy"])) * 100, 2),
            "macro_f1": round(float(np.mean(cv_base["test_f1_macro"])) * 100, 2),
        },
        "enhanced_features": {
            "feature_count": len(ALL_FEATURES_WITH_ENGINEERED),
            "cv_accuracy": round(float(np.mean(cv_enhanced["test_accuracy"])) * 100, 2),
            "macro_f1": round(float(np.mean(cv_enhanced["test_f1_macro"])) * 100, 2),
        },
        "feature_importances": importances,
    }


def main():
    parser = argparse.ArgumentParser(description="Run temporal feature engineering & benchmark.")
    parser.add_argument(
        "--file",
        type=str,
        default=str(RAW_DATA_DIR / "synthetic_machine_data.csv"),
        help="Path to sensor dataset CSV",
    )
    args = parser.parse_args()

    print("Running Temporal Feature Engineering Benchmark...")
    results = compare_feature_sets(args.file)

    print("\n" + "=" * 70)
    print(" FEATURE ENGINEERING BENCHMARK COMPARISON")
    print("=" * 70)
    print(f"1. Base Model (5 Sensors)     : Accuracy = {results['baseline_features']['cv_accuracy']}%, Macro F1 = {results['baseline_features']['macro_f1']}%")
    print(f"2. Enhanced Model (12 Features): Accuracy = {results['enhanced_features']['cv_accuracy']}%, Macro F1 = {results['enhanced_features']['macro_f1']}%")

    print("\nEnhanced Feature Importance Rankings:")
    for feat, imp in results["feature_importances"].items():
        tag = "[ENGINEERED]" if feat in ENGINEERED_FEATURE_NAMES else "[RAW SENSOR]"
        print(f"  {feat:22s} {tag:14s}: {imp:6.2f}%")

    print("\n" + "=" * 70)
    print(" PHYSICAL RATIONALE FOR ENGINEERED FEATURES:")
    print("=" * 70)
    print(" * temperature_rate: Rapid positive slope (dT/dt) detects heat surges before absolute threshold trip.")
    print(" * rolling_current : Dampens ACS712 inductive noise spikes during motor commutation.")
    print(" * rolling_vibration: Smoothes MPU6050 accelerometer jitter for continuous trend estimation.")
    print(" * rpm_change      : Detects sudden deceleration load spikes under binding.")
    print("=" * 70)


if __name__ == "__main__":
    main()
