"""Model Evaluation and Diagnostics Module for Industrial Machine AI Subsystem.

Evaluates the trained model on holdout test telemetry (test.csv), generates
confusion matrix and feature importance visualizations, computes per-class metrics,
and analyzes False Negatives vs False Positives.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    PROCESSED_DATA_DIR,
    PLOTS_DIR,
    MODEL_FILE,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
    STATUS_NAMES,
)
from src.train import load_model

# Clean plot aesthetics
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: list,
    output_path: Path,
):
    """Plots an annotated Confusion Matrix heatmap."""
    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=150)
    cax = ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.85)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > cm.max() / 2 else "black"
            ax.text(
                j,
                i,
                f"{val}",
                ha="center",
                va="center",
                color=color,
                fontsize=13,
                fontweight="bold",
            )

    fig.colorbar(cax, shrink=0.8)
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, fontsize=10)
    ax.set_yticklabels(class_names, fontsize=10)

    ax.set_xlabel("Predicted Machine Condition", fontsize=11, labelpad=10)
    ax.set_ylabel("Actual Machine Condition", fontsize=11, labelpad=10)
    ax.set_title("Test Set Confusion Matrix", fontsize=13, fontweight="bold", pad=15)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_feature_importance(
    importances: Dict[str, float],
    output_path: Path,
):
    """Plots a clean horizontal bar chart of feature contributions."""
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    features = [item[0].upper() for item in sorted_items]
    values = [item[1] * 100 for item in sorted_items]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    bars = ax.barh(features[::-1], values[::-1], color="#1f77b4", edgecolor="#0e4b75", height=0.6)

    # Annotate bars with percentage values
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.6,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xlim(0, max(values) + 8)
    ax.set_xlabel("Contribution / Importance (%)", fontsize=10)
    ax.set_title("Random Forest Sensor Feature Importance", fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    # Subtitle note on causation
    plt.figtext(
        0.5,
        -0.02,
        "Note: Feature importance shows which input variables contributed most to the model's decisions.\nIt indicates predictive correlation, not physical causation.",
        wrap=True,
        horizontalalignment="center",
        fontsize=8,
        style="italic",
        color="#555555",
    )

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def evaluate_model(
    test_csv: Path | str = PROCESSED_DATA_DIR / "test.csv",
    model_path: Path | str = MODEL_FILE,
    plots_dir: Path | str = PLOTS_DIR,
) -> Dict[str, Any]:
    """Evaluates the trained model on holdout test data and creates diagnostic plots."""
    test_path = Path(test_csv)
    m_path = Path(model_path)
    p_dir = Path(plots_dir)

    p_dir.mkdir(parents=True, exist_ok=True)

    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset not found at: {test_path}")

    test_df = pd.read_csv(test_path)
    X_test = test_df[SENSOR_FEATURES]
    y_test = test_df[TARGET_COLUMN].astype(int)

    model = load_model(m_path)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # Core Metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))

    # Fault Specific Recall (Critical Metric)
    fault_idx = 2
    fault_mask = y_test == fault_idx
    fault_actual_count = int(fault_mask.sum())
    fault_correct_count = int((y_pred[fault_mask] == fault_idx).sum())
    fault_recall = fault_correct_count / fault_actual_count if fault_actual_count > 0 else 1.0

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    cm_plot_path = p_dir / "confusion_matrix.png"
    plot_confusion_matrix(cm, STATUS_NAMES, cm_plot_path)

    # Feature Importance Plot
    feature_importances = {
        feat: float(imp) for feat, imp in zip(SENSOR_FEATURES, model.feature_importances_)
    }
    fi_plot_path = p_dir / "feature_importance.png"
    plot_feature_importance(feature_importances, fi_plot_path)

    # Per Class Report
    report_dict = classification_report(
        y_test,
        y_pred,
        target_names=STATUS_NAMES,
        output_dict=True,
        zero_division=0,
    )

    return {
        "total_test_samples": len(test_df),
        "accuracy": acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "macro_f1": f1_macro,
        "fault_recall": fault_recall,
        "confusion_matrix": cm.tolist(),
        "classification_report": report_dict,
        "feature_importances": feature_importances,
        "plots": {
            "confusion_matrix": cm_plot_path,
            "feature_importance": fi_plot_path,
        },
    }


def print_evaluation_summary(results: Dict[str, Any]):
    """Prints a structured evaluation summary to console."""
    print("=" * 65)
    print(" MODEL EVALUATION REPORT (Holdout Test Set: 240 samples)")
    print("=" * 65)
    print(f"Overall Accuracy        : {results['accuracy'] * 100:.2f}%")
    print(f"Macro Precision         : {results['precision_macro'] * 100:.2f}%")
    print(f"Macro Recall            : {results['recall_macro'] * 100:.2f}%")
    print(f"Macro F1-Score          : {results['f1_macro'] * 100:.2f}%")
    print(f"CRITICAL FAULT RECALL   : {results['fault_recall'] * 100:.2f}%")

    print("\nPer-Class Performance Breakdown:")
    print(f"{'Condition':12s} {'Precision':>10s} {'Recall':>10s} {'F1-Score':>10s} {'Support':>10s}")
    print("-" * 55)
    for name in STATUS_NAMES:
        m = results["classification_report"][name]
        print(
            f"{name:12s} {m['precision']*100:9.1f}% {m['recall']*100:9.1f}% {m['f1-score']*100:9.1f}% {int(m['support']):10d}"
        )

    print("\nConfusion Matrix (Actual Rows vs Predicted Columns):")
    cm = np.array(results["confusion_matrix"])
    print(f"{'':12s} {'Pred NORMAL':>12s} {'Pred WARNING':>14s} {'Pred FAULT':>12s}")
    for i, name in enumerate(STATUS_NAMES):
        print(f"Act {name:8s} {cm[i, 0]:12d} {cm[i, 1]:14d} {cm[i, 2]:12d}")

    print("\n" + "=" * 65)
    print(" ENGINEERING RISK ANALYSIS: False Positives vs False Negatives")
    print("=" * 65)
    print("1. False Negative (FN) for FAULT: [MOST CRITICAL]")
    print("   -> The machine is in FAULT state, but the AI incorrectly predicts NORMAL/WARNING.")
    print("   -> Impact: Catastrophic motor burn-out, production downtime, safety hazard.")
    print("2. False Positive (FP) for FAULT: [MILD INCONVENIENCE]")
    print("   -> The machine is running fine, but the AI sounds a false alarm.")
    print("   -> Impact: Maintenance technician inspects the machine; no damage occurs.")
    print("=> Therefore, in predictive maintenance, high FAULT RECALL is paramount.")
    print("=" * 65)
    print(f"[OK] Confusion matrix plot saved   : {results['plots']['confusion_matrix']}")
    print(f"[OK] Feature importance plot saved : {results['plots']['feature_importance']}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate model on holdout test set.")
    parser.add_argument(
        "--test-data",
        type=str,
        default=str(PROCESSED_DATA_DIR / "test.csv"),
        help="Path to preprocessed test.csv",
    )
    args = parser.parse_args()

    results = evaluate_model(test_csv=args.test_data)
    print_evaluation_summary(results)


if __name__ == "__main__":
    main()
