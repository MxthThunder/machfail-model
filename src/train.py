"""Model Training and Benchmark Module for Industrial Machine AI Subsystem.

Trains baseline (DummyClassifier) and candidate ML models (Logistic Regression,
Decision Tree, Random Forest, Gradient Boosting) using Stratified K-Fold CV,
selects the primary RandomForestClassifier, and serializes model artifacts and metadata.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    MODEL_FILE,
    METADATA_FILE,
    SCALER_FILE,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
    RANDOM_SEED,
)
from src.preprocessing import load_scaler, scale_features


def get_candidate_models() -> Dict[str, Any]:
    """Returns the dictionary of baseline and candidate classification models."""
    return {
        "Dummy (Baseline)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=6,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100,
            max_depth=4,
            random_state=RANDOM_SEED,
        ),
    }


def benchmark_candidate_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_splits: int = 5,
) -> pd.DataFrame:
    """Evaluates all candidate models using 5-Fold Stratified Cross-Validation on training data.

    Returns a summary DataFrame comparing Accuracy, Macro Precision, Macro Recall, and Macro F1.
    """
    scaler = load_scaler(SCALER_FILE)
    X_train_scaled = scale_features(X_train, scaler)

    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    models = get_candidate_models()
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)

    scoring = {
        "accuracy": "accuracy",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "f1_macro": "f1_macro",
    }

    results = []

    for model_name, model in models.items():
        # Logistic Regression benefits from standardized features; trees work on raw or scaled
        features_to_use = X_train_scaled if model_name == "Logistic Regression" else X_train

        cv_res = cross_validate(
            model,
            features_to_use,
            y_train,
            cv=skf,
            scoring=scoring,
            n_jobs=-1,
        )

        results.append(
            {
                "Model": model_name,
                "CV Accuracy (%)": round(float(np.mean(cv_res["test_accuracy"])) * 100, 2),
                "Macro Precision (%)": round(float(np.mean(cv_res["test_precision_macro"])) * 100, 2),
                "Macro Recall (%)": round(float(np.mean(cv_res["test_recall_macro"])) * 100, 2),
                "Macro F1-Score (%)": round(float(np.mean(cv_res["test_f1_macro"])) * 100, 2),
            }
        )

    return pd.DataFrame(results)


def train_and_save_final_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_path: Path = MODEL_FILE,
    metadata_path: Path = METADATA_FILE,
    hyperparameters: Dict[str, Any] = None,
) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    """Trains the primary RandomForestClassifier on full training data and persists model & metadata."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    if hyperparameters is None:
        hyperparameters = {
            "n_estimators": 100,
            "max_depth": 6,
            "min_samples_split": 4,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": RANDOM_SEED,
        }

    model = RandomForestClassifier(**hyperparameters)
    model.fit(X_train[SENSOR_FEATURES], y_train)

    # Serialize model artifact
    joblib.dump(model, model_path)

    # Calculate training performance
    y_pred_train = model.predict(X_train[SENSOR_FEATURES])
    train_acc = float(accuracy_score(y_train, y_pred_train))
    train_macro_f1 = float(f1_score(y_train, y_pred_train, average="macro"))
    train_fault_recall = float(
        recall_score(y_train, y_pred_train, labels=[2], average="macro", zero_division=0)
    )

    # Feature importance
    feature_importances = {
        feat: round(float(imp), 4)
        for feat, imp in zip(SENSOR_FEATURES, model.feature_importances_)
    }

    # Structured metadata
    metadata = {
        "model_name": "RandomForestClassifier",
        "model_version": "1.0.0",
        "training_date": datetime.now().isoformat(),
        "dataset_type": "synthetic",
        "data_source_note": "Trained on synthetic development telemetry. Retrain before production on real machine data.",
        "feature_names": SENSOR_FEATURES,
        "class_mapping": STATUS_MAP,
        "classes": [int(c) for c in model.classes_],
        "hyperparameters": {k: str(v) if isinstance(v, (type, type(None))) else v for k, v in hyperparameters.items()},
        "dataset_size": {
            "train_samples": len(X_train),
            "class_distribution_train": {
                STATUS_MAP[k]: int(v)
                for k, v in y_train.value_counts().sort_index().items()
            },
        },
        "training_metrics": {
            "accuracy": round(train_acc, 4),
            "macro_f1": round(train_macro_f1, 4),
            "fault_recall": round(train_fault_recall, 4),
        },
        "feature_importances": feature_importances,
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    return model, metadata


def load_model(model_path: Path = MODEL_FILE) -> RandomForestClassifier:
    """Loads a serialized trained model from disk."""
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model artifact not found at: {model_path}")
    return joblib.load(model_path)


def load_metadata(metadata_path: Path = METADATA_FILE) -> Dict[str, Any]:
    """Loads model metadata JSON from disk."""
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found at: {metadata_path}")
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Train baseline and ML models for predictive maintenance.")
    parser.add_argument(
        "--train-data",
        type=str,
        default=str(PROCESSED_DATA_DIR / "train.csv"),
        help="Path to preprocessed train.csv",
    )
    args = parser.parse_args()

    train_path = Path(args.train_data)
    if not train_path.exists():
        print(f"[ERROR] Processed training file not found at {train_path}. Run preprocessing first.")
        sys.exit(1)

    print(f"Loading training data from: {train_path}")
    train_df = pd.read_csv(train_path)
    X_train = train_df[SENSOR_FEATURES]
    y_train = train_df[TARGET_COLUMN].astype(int)

    print("\n" + "=" * 60)
    print(" 1. BENCHMARKING BASELINE & CANDIDATE MODELS (5-Fold CV)")
    print("=" * 60)
    benchmark_df = benchmark_candidate_models(X_train, y_train, n_splits=5)
    print(benchmark_df.to_string(index=False))

    print("\n" + "=" * 60)
    print(" 2. TRAINING & PERSISTING PRIMARY RANDOM FOREST MODEL")
    print("=" * 60)
    model, metadata = train_and_save_final_model(X_train, y_train)

    print(f"[OK] Model saved to: {MODEL_FILE}")
    print(f"[OK] Metadata saved to: {METADATA_FILE}")
    print(f"\nTraining Set Accuracy   : {metadata['training_metrics']['accuracy'] * 100:.2f}%")
    print(f"Training Set Macro F1   : {metadata['training_metrics']['macro_f1'] * 100:.2f}%")
    print(f"Training Set Fault Recall: {metadata['training_metrics']['fault_recall'] * 100:.2f}%")
    print("\nTrained Feature Importances:")
    for feat, imp in metadata["feature_importances"].items():
        print(f"  - {feat:12s}: {imp * 100:6.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
