import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DATA_DIR, PLOTS_DIR, MODEL_FILE
from src.evaluate import evaluate_model


def test_model_evaluation_metrics_and_plots():
    """Verify test set evaluation produces high-quality metrics and saves plots."""
    test_csv = PROCESSED_DATA_DIR / "test.csv"
    assert test_csv.exists(), "test.csv must exist to run evaluation test"
    assert MODEL_FILE.exists(), "model.joblib must exist to run evaluation test"

    results = evaluate_model(test_csv=test_csv)

    # Check metric thresholds
    assert results["accuracy"] >= 0.95, f"Accuracy too low: {results['accuracy']}"
    assert results["macro_f1"] >= 0.95, f"Macro F1 too low: {results['macro_f1']}"
    assert results["fault_recall"] >= 0.95, f"Fault recall must be near-perfect: {results['fault_recall']}"

    # Check Confusion Matrix structure
    cm = results["confusion_matrix"]
    assert len(cm) == 3
    assert len(cm[0]) == 3

    # Check plots exist and are non-empty
    cm_plot = PLOTS_DIR / "confusion_matrix.png"
    fi_plot = PLOTS_DIR / "feature_importance.png"

    assert cm_plot.exists(), "confusion_matrix.png was not generated"
    assert cm_plot.stat().st_size > 1000, "confusion_matrix.png is empty"

    assert fi_plot.exists(), "feature_importance.png was not generated"
    assert fi_plot.stat().st_size > 1000, "feature_importance.png is empty"


if __name__ == "__main__":
    test_model_evaluation_metrics_and_plots()
    print("All Stage 7 model evaluation tests passed successfully!")
