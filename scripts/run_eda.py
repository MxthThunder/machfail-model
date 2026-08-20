"""Exploratory Data Analysis (EDA) & Visualization Generator.

Generates 8 diagnostic charts illustrating machine health patterns,
physics correlations, and class distributions over time.
Saved directly into `data/processed/plots/`.
"""

import argparse
import sys
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    RAW_DATA_DIR,
    PLOTS_DIR,
    SENSOR_FEATURES,
    STATUS_MAP,
    RANDOM_SEED,
)
from src.data_loader import load_and_validate

# Clean plot aesthetics configuration
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.alpha"] = 0.4
plt.rcParams["grid.linestyle"] = "--"

# Color palette for conditions: 0=Green (Normal), 1=Orange (Warning), 2=Red (Fault)
COLOR_PALETTE = {
    0: "#2ca02c",  # Green: Normal
    1: "#ff7f0e",  # Orange: Warning
    2: "#d62728",  # Red: Fault
}


def setup_plots_directory() -> Path:
    """Ensures the plots output directory exists."""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return PLOTS_DIR


def plot_sensor_over_time(
    df: pd.DataFrame,
    sensor: str,
    unit: str,
    plot_path: Path,
    max_points: int = 400,
):
    """Plots sensor time series with status background shading."""
    plot_df = df.iloc[:max_points].copy()
    x = range(len(plot_df))

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)

    # Plot sensor trace
    ax.plot(x, plot_df[sensor], color="#1f77b4", linewidth=1.5, label=f"Measured {sensor.upper()} ({unit})")

    # Add background color bands for machine state
    for status_val, label in STATUS_MAP.items():
        mask = plot_df["status"] == status_val
        if mask.any():
            ax.scatter(
                np.array(x)[mask],
                plot_df[sensor][mask],
                color=COLOR_PALETTE[status_val],
                s=12,
                alpha=0.6,
                label=f"State: {label}",
            )

    ax.set_title(f"Machine Telemetry: {sensor.upper()} Over Time", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Time (Consecutive Operational Minutes)", fontsize=10)
    ax.set_ylabel(f"{sensor.capitalize()} ({unit})", fontsize=10)
    ax.grid(True)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=8)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()


def plot_scatter_correlation(
    df: pd.DataFrame,
    x_col: str,
    x_unit: str,
    y_col: str,
    y_unit: str,
    plot_path: Path,
):
    """Scatter plot demonstrating multi-sensor physical correlation across machine conditions."""
    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)

    for status_val, label in STATUS_MAP.items():
        subset = df[df["status"] == status_val]
        ax.scatter(
            subset[x_col],
            subset[y_col],
            color=COLOR_PALETTE[status_val],
            label=f"{label} (n={len(subset)})",
            alpha=0.65,
            edgecolors="none",
            s=28,
        )

    ax.set_title(
        f"Correlation: {x_col.upper()} vs {y_col.upper()}",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax.set_xlabel(f"{x_col.capitalize()} ({x_unit})", fontsize=10)
    ax.set_ylabel(f"{y_col.capitalize()} ({y_unit})", fontsize=10)
    ax.grid(True)
    ax.legend(title="Machine Condition", loc="best", framealpha=0.9)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()


def plot_sensor_distributions(df: pd.DataFrame, plot_path: Path):
    """Generates multi-panel boxplots showing distributions of all 5 sensors across machine conditions."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), dpi=150)
    axes = axes.flatten()

    units = {
        "rpm": "RPM",
        "temperature": "°C",
        "humidity": "%",
        "current": "A",
        "vibration": "g",
    }

    for idx, feature in enumerate(SENSOR_FEATURES):
        ax = axes[idx]
        data_to_plot = [
            df[df["status"] == status_val][feature].values
            for status_val in sorted(STATUS_MAP.keys())
        ]

        bplot = ax.boxplot(
            data_to_plot,
            tick_labels=[STATUS_MAP[s] for s in sorted(STATUS_MAP.keys())],
            patch_artist=True,
            medianprops=dict(color="black", linewidth=1.5),
        )

        for patch, status_val in zip(bplot["boxes"], sorted(STATUS_MAP.keys())):
            patch.set_facecolor(COLOR_PALETTE[status_val])
            patch.set_alpha(0.7)

        ax.set_title(f"{feature.upper()} Distribution", fontsize=11, fontweight="bold")
        ax.set_ylabel(f"{feature.capitalize()} ({units[feature]})", fontsize=9)
        ax.grid(True, axis="y")

    # Remove the unused 6th subplot
    fig.delaxes(axes[5])

    plt.suptitle("Sensor Value Distributions Across Operating Conditions", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()


def generate_all_plots(df: pd.DataFrame, output_dir: Path) -> List[Path]:
    """Generates all 8 required exploratory data analysis plots."""
    setup_plots_directory()
    saved_plots = []

    # 1. RPM over time
    p1 = output_dir / "01_rpm_over_time.png"
    plot_sensor_over_time(df, "rpm", "RPM", p1)
    saved_plots.append(p1)

    # 2. Temperature over time
    p2 = output_dir / "02_temperature_over_time.png"
    plot_sensor_over_time(df, "temperature", "°C", p2)
    saved_plots.append(p2)

    # 3. Current over time
    p3 = output_dir / "03_current_over_time.png"
    plot_sensor_over_time(df, "current", "A", p3)
    saved_plots.append(p3)

    # 4. Vibration over time
    p4 = output_dir / "04_vibration_over_time.png"
    plot_sensor_over_time(df, "vibration", "g", p4)
    saved_plots.append(p4)

    # 5. Humidity over time
    p5 = output_dir / "05_humidity_over_time.png"
    plot_sensor_over_time(df, "humidity", "%", p5)
    saved_plots.append(p5)

    # 6. RPM vs Temperature
    p6 = output_dir / "06_rpm_vs_temperature.png"
    plot_scatter_correlation(df, "rpm", "RPM", "temperature", "°C", p6)
    saved_plots.append(p6)

    # 7. Current vs Vibration
    p7 = output_dir / "07_current_vs_vibration.png"
    plot_scatter_correlation(df, "current", "A", "vibration", "g", p7)
    saved_plots.append(p7)

    # 8. Sensor Distributions by Machine Status
    p8 = output_dir / "08_sensor_distributions_by_status.png"
    plot_sensor_distributions(df, p8)
    saved_plots.append(p8)

    return saved_plots


def main():
    parser = argparse.ArgumentParser(description="Generate Exploratory Data Analysis (EDA) visualizations.")
    parser.add_argument(
        "--file",
        type=str,
        default=str(RAW_DATA_DIR / "synthetic_machine_data.csv"),
        help="Path to validated sensor dataset CSV",
    )
    args = parser.parse_args()

    print(f"Loading dataset: {args.file}")
    df, report = load_and_validate(args.file)
    if not report.is_valid:
        print("[WARNING] Dataset has validation warnings, proceeding with clean records.")

    print(f"Generating 8 EDA visualizations into: {PLOTS_DIR}")
    plots = generate_all_plots(df, PLOTS_DIR)

    print("\n[OK] Successfully generated all 8 EDA plots:")
    for p in plots:
        print(f"  - {p.name}")


if __name__ == "__main__":
    main()
