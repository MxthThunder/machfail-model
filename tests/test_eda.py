import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_DIR, PLOTS_DIR
from src.data_loader import load_and_validate
from scripts.run_eda import generate_all_plots


def test_eda_plot_generation():
    """Verify that all 8 required EDA diagnostic plots are generated and non-empty."""
    csv_path = RAW_DATA_DIR / "synthetic_machine_data.csv"
    assert csv_path.exists(), "Dataset must exist to run EDA tests"

    df, report = load_and_validate(csv_path)
    assert report.is_valid is True

    saved_plots = generate_all_plots(df, PLOTS_DIR)

    # We expect exactly 8 diagnostic plots
    assert len(saved_plots) == 8, f"Expected 8 plots, got {len(saved_plots)}"

    expected_plot_names = [
        "01_rpm_over_time.png",
        "02_temperature_over_time.png",
        "03_current_over_time.png",
        "04_vibration_over_time.png",
        "05_humidity_over_time.png",
        "06_rpm_vs_temperature.png",
        "07_current_vs_vibration.png",
        "08_sensor_distributions_by_status.png",
    ]

    for name in expected_plot_names:
        plot_file = PLOTS_DIR / name
        assert plot_file.exists(), f"Plot file {name} was not generated!"
        assert plot_file.stat().st_size > 1000, f"Plot file {name} is unusually small or empty!"


if __name__ == "__main__":
    test_eda_plot_generation()
    print("All Stage 4 EDA tests passed successfully!")
