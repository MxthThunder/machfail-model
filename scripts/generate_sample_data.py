"""Synthetic Dataset Generator for Industrial Machine AI Subsystem.

Generates realistic, physically correlated machine sensor readings for a DC motor
monitoring system equipped with IR (RPM), DHT22 (Temp/Humidity), ACS712 (Current),
and MPU6050 (Vibration) sensors.

NOTE: This dataset is SYNTHETIC and designed for initial development and testing.
It is explicitly tagged with `data_source='synthetic'`.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    SAMPLE_DATA_DIR,
    RANDOM_SEED,
    STATUS_MAP,
)


def generate_synthetic_dataset(
    n_samples: int = 1200,
    random_seed: int = RANDOM_SEED,
    start_time: str = "2026-08-20T08:00:00",
) -> pd.DataFrame:
    """Generates synthetic time-series sensor data with realistic physical correlations.

    Parameters
    ----------
    n_samples : int
        Number of consecutive 1-minute telemetry records to generate (default: 1200).
    random_seed : int
        Random seed for reproducibility.
    start_time : str
        ISO-8601 start timestamp for the simulation.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: timestamp, rpm, temperature, humidity, current, vibration, status, data_source.
    """
    np.random.seed(random_seed)

    # Time series timestamps (1-minute intervals)
    base_dt = datetime.fromisoformat(start_time)
    timestamps = [base_dt + timedelta(minutes=i) for i in range(n_samples)]

    # We simulate realistic operational episodes:
    # 0 = NORMAL (~65%), 1 = WARNING (~22%), 2 = FAULT (~13%)
    # Consecutive segments mimic real machine runs
    statuses = []
    current_state = 0
    state_durations = {0: (30, 80), 1: (15, 35), 2: (10, 25)}

    remaining = n_samples
    while remaining > 0:
        duration = np.random.randint(*state_durations[current_state])
        duration = min(duration, remaining)
        statuses.extend([current_state] * duration)
        remaining -= duration

        # State transition logic
        if current_state == 0:
            current_state = np.random.choice([0, 1], p=[0.25, 0.75])
        elif current_state == 1:
            current_state = np.random.choice([0, 2], p=[0.35, 0.65])
        else:  # from fault (simulating motor cooldown / intervention)
            current_state = 0

    statuses = np.array(statuses[:n_samples])

    # Generate correlated physics-based features based on operational state
    rpms = []
    temps = []
    humidities = []
    currents = []
    vibrations = []

    # Ambient baseline conditions
    ambient_temp = 28.5 + np.random.normal(0, 0.5, size=n_samples)
    ambient_humidity = 60.0 + np.random.normal(0, 2.0, size=n_samples)

    for i, state in enumerate(statuses):
        if state == 0:
            # NORMAL: Stable nominal speed, low vibration, nominal current, stable temp
            rpm = np.random.normal(loc=1500, scale=20)
            current = np.random.normal(loc=0.72, scale=0.03)
            vibration = np.random.normal(loc=0.10, scale=0.02)
            temp = ambient_temp[i] + 4.0 + (current * 4.0) + np.random.normal(0, 0.3)
            humidity = ambient_humidity[i] + np.random.normal(0, 0.8)

        elif state == 1:
            # WARNING: Mild mechanical friction/load -> speed drops, current & vibration rise, temp builds up
            rpm = np.random.normal(loc=1390, scale=35)
            current = np.random.normal(loc=0.98, scale=0.06)
            vibration = np.random.normal(loc=0.28, scale=0.04)
            temp = ambient_temp[i] + 9.0 + (current * 7.0) + np.random.normal(0, 0.6)
            humidity = ambient_humidity[i] + np.random.normal(0, 1.0)

        else:
            # FAULT: Severe overload / impending stall -> steep RPM collapse, high current draw, extreme vibration, heavy thermal rise
            rpm = np.random.normal(loc=1020, scale=80)
            current = np.random.normal(loc=1.45, scale=0.12)
            vibration = np.random.normal(loc=0.55, scale=0.08)
            temp = ambient_temp[i] + 16.0 + (current * 10.0) + np.random.normal(0, 1.0)
            humidity = ambient_humidity[i] + np.random.normal(0, 1.2)

        # Clip values to physically realistic lower bounds
        rpm = max(0.0, rpm)
        current = max(0.0, current)
        vibration = max(0.0, vibration)
        temp = max(0.0, temp)
        humidity = np.clip(humidity, 0.0, 100.0)

        rpms.append(round(float(rpm), 1))
        currents.append(round(float(current), 2))
        vibrations.append(round(float(vibration), 3))
        temps.append(round(float(temp), 1))
        humidities.append(round(float(humidity), 1))

    df = pd.DataFrame(
        {
            "timestamp": [t.isoformat() for t in timestamps],
            "rpm": rpms,
            "temperature": temps,
            "humidity": humidities,
            "current": currents,
            "vibration": vibrations,
            "status": statuses,
            "data_source": "synthetic",
        }
    )

    return df


def save_sample_json_payloads():
    """Generates typical sample payloads for testing API and presentations."""
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    samples = {
        "normal_reading.json": {
            "rpm": 1505.0,
            "temperature": 31.8,
            "humidity": 59.5,
            "current": 0.71,
            "vibration": 0.102,
        },
        "warning_reading.json": {
            "rpm": 1380.0,
            "temperature": 43.5,
            "humidity": 62.0,
            "current": 0.99,
            "vibration": 0.285,
        },
        "fault_reading.json": {
            "rpm": 980.0,
            "temperature": 56.4,
            "humidity": 64.2,
            "current": 1.52,
            "vibration": 0.610,
        },
    }

    for filename, payload in samples.items():
        filepath = SAMPLE_DATA_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
    print(f"Generated {len(samples)} sample JSON payloads in {SAMPLE_DATA_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic machine sensor dataset.")
    parser.add_argument(
        "--samples",
        type=int,
        default=1200,
        help="Number of records to generate (default: 1200)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(RAW_DATA_DIR / "synthetic_machine_data.csv"),
        help="Path to output CSV file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=f"Random seed (default: {RANDOM_SEED})",
    )
    args = parser.parse_args()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output)

    print(f"Generating {args.samples} synthetic machine telemetry records (seed={args.seed})...")
    df = generate_synthetic_dataset(n_samples=args.samples, random_seed=args.seed)

    df.to_csv(out_path, index=False)
    print(f"Saved synthetic dataset successfully to: {out_path}")
    print("\nDataset Summary:")
    print(f"- Total Records: {len(df)}")
    print("- Class Distribution:")
    for status_code, count in df["status"].value_counts().sort_index().items():
        name = STATUS_MAP.get(status_code, "UNKNOWN")
        pct = (count / len(df)) * 100
        print(f"  [{status_code}] {name:8s}: {count:4d} rows ({pct:.1f}%)")

    # Generate sample fixtures for API / testing
    save_sample_json_payloads()


if __name__ == "__main__":
    main()
