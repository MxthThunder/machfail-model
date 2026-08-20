"""Data Loading and Validation Module for Industrial Machine AI Subsystem.

Provides robust CSV loading, schema verification, out-of-bounds checking,
and transparent validation reporting.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
    SENSOR_RANGES,
)


@dataclass
class ValidationReport:
    """Structured report holding data validation results."""

    is_valid: bool = True
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    column_stats: Dict[str, Any] = field(default_factory=dict)

    def print_summary(self):
        """Prints a human-readable validation summary."""
        print("=" * 60)
        print(" DATA VALIDATION REPORT")
        print("=" * 60)
        print(f"Overall Status   : {'PASSED (Valid)' if self.is_valid else 'FAILED (Issues Detected)'}")
        print(f"Total Records    : {self.total_records}")
        print(f"Valid Records    : {self.valid_records}")
        print(f"Invalid Records  : {self.invalid_records}")

        if self.errors:
            print("\n[ERROR] Critical Violations:")
            for err in self.errors:
                print(f"  - {err}")

        if self.warnings:
            print("\n[WARNING] Advisory Notices:")
            for warn in self.warnings:
                print(f"  - {warn}")

        if not self.errors and not self.warnings:
            print("\n[OK] All schema checks, sensor bounds, and label constraints passed!")
        print("=" * 60)


def load_raw_csv(filepath: Path | str) -> pd.DataFrame:
    """Loads a CSV file into a pandas DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is empty or unparseable.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Dataset file is empty: {path}")

    return df


def validate_dataframe(
    df: pd.DataFrame,
    check_target: bool = True,
) -> Tuple[pd.DataFrame, ValidationReport]:
    """Performs deep validation on machine telemetry data.

    Checks performed:
    1. Schema & Required Columns.
    2. Missing / NaN values.
    3. Duplicate Timestamps.
    4. Sensor Physical Range Bounds (RPM, Temp, Humidity, Current, Vibration).
    5. Target Class Integrity (status values must be in {0, 1, 2}).

    Parameters
    ----------
    df : pd.DataFrame
        Input telemetry DataFrame.
    check_target : bool
        Whether to validate the target column `status` (default: True).

    Returns
    -------
    Tuple[pd.DataFrame, ValidationReport]
        Filtered clean DataFrame (records passing all checks) and the ValidationReport.
    """
    report = ValidationReport(total_records=len(df))
    valid_mask = pd.Series(True, index=df.index)

    # 1. Check Required Sensor Columns
    missing_cols = [col for col in SENSOR_FEATURES if col not in df.columns]
    if missing_cols:
        report.errors.append(f"Missing required sensor columns: {missing_cols}")
        report.is_valid = False
        return df, report

    # 2. Check for Missing Values (NaN / Null)
    for col in SENSOR_FEATURES:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            report.errors.append(f"'{col}' contains {null_count} missing (NaN) values.")
            valid_mask &= df[col].notna()

    # 3. Check Timestamp integrity & duplicates
    if "timestamp" in df.columns:
        duplicate_ts_count = int(df["timestamp"].duplicated().sum())
        if duplicate_ts_count > 0:
            report.warnings.append(f"Found {duplicate_ts_count} duplicate timestamp records.")
            # Note: We flag duplicate timestamps as warnings unless identical rows
    else:
        report.warnings.append("No 'timestamp' column found in dataset.")

    # 4. Check Physical Sensor Ranges
    for col in SENSOR_FEATURES:
        if col not in df.columns:
            continue

        bounds = SENSOR_RANGES[col]
        min_val = bounds["min"]
        max_val = bounds["max"]
        unit = bounds["unit"]

        # Negative / below minimum check
        below_min = df[col] < min_val
        below_min_count = int(below_min.sum())
        if below_min_count > 0:
            report.errors.append(
                f"'{col}' contains {below_min_count} values below physical limit ({min_val} {unit})."
            )
            valid_mask &= ~below_min

        # Above maximum check
        above_max = df[col] > max_val
        above_max_count = int(above_max.sum())
        if above_max_count > 0:
            report.errors.append(
                f"'{col}' contains {above_max_count} values exceeding physical limit ({max_val} {unit})."
            )
            valid_mask &= ~above_max

        # Collect summary stats for report
        report.column_stats[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "unit": unit,
        }

    # 5. Check Target Labels (if present)
    if check_target and TARGET_COLUMN in df.columns:
        valid_classes = set(STATUS_MAP.keys())
        # Check for non-numeric or out-of-set classes
        invalid_labels = ~df[TARGET_COLUMN].isin(valid_classes)
        invalid_labels_count = int(invalid_labels.sum())
        if invalid_labels_count > 0:
            bad_values = df[invalid_labels][TARGET_COLUMN].unique().tolist()
            report.errors.append(
                f"'{TARGET_COLUMN}' contains {invalid_labels_count} invalid label(s): {bad_values}. Allowed: {valid_classes}."
            )
            valid_mask &= ~invalid_labels

    report.valid_records = int(valid_mask.sum())
    report.invalid_records = report.total_records - report.valid_records
    if report.invalid_records > 0 or len(report.errors) > 0:
        report.is_valid = False

    clean_df = df[valid_mask].copy()
    return clean_df, report


def load_and_validate(
    filepath: Path | str,
    check_target: bool = True,
) -> Tuple[pd.DataFrame, ValidationReport]:
    """Convenience helper to load a CSV and immediately validate it.

    Parameters
    ----------
    filepath : Path | str
        Path to the CSV file.
    check_target : bool
        Whether to check target class integrity.

    Returns
    -------
    Tuple[pd.DataFrame, ValidationReport]
        Clean validated DataFrame and the full ValidationReport.
    """
    raw_df = load_raw_csv(filepath)
    clean_df, report = validate_dataframe(raw_df, check_target=check_target)
    return clean_df, report


def main():
    parser = argparse.ArgumentParser(description="Load and validate machine telemetry dataset.")
    parser.add_argument(
        "--file",
        type=str,
        default=str(RAW_DATA_DIR / "synthetic_machine_data.csv"),
        help="Path to CSV dataset to validate",
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    print(f"Loading and validating dataset: {file_path}")

    try:
        clean_df, report = load_and_validate(file_path)
        report.print_summary()
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
