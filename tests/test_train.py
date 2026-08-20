"""Stage 6 Model Training & Persistence Unit Tests."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    PROCESSED_DATA_DIR,
    MODEL_FILE,
    METADATA_FILE,
    SENSOR_FEATURES,
    TARGET_COLUMN,
    STATUS_MAP,
)
from src.train import (
    get_candidate_models,
    benchmark_candidate_models,
    train_and_save_final_model,
    load_model,
    load_metadata,
)


def test_candidate_models_dict():
    """Verify all 5 candidate models are registered."""
    models = get_candidate_models()
    expected = [
        "Dummy (Baseline)",
        "Logistic Regression",
        "Decision Tree",
        "Random Forest",
        "Gradient Boosting",
    ]
    for m in expected:
        assert m in models, f"Model '{m}' missing from candidate models dictionary"


def test_benchmark_candidate_models():
    """Verify CV benchmarking runs and returns expected columns."""
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
    X_train = train_df[SENSOR_FEATURES]
    y_train = train_df[TARGET_COLUMN].astype(int)

    benchmark_df = benchmark_candidate_models(X_train, y_train, n_splits=3)
    assert len(benchmark_df) == 5
    assert "Model" in benchmark_df.columns
    assert "CV Accuracy (%)" in benchmark_df.columns
    assert "Macro F1-Score (%)" in benchmark_df.columns


def test_train_and_save_final_model():
    """Verify Random Forest training, file persistence, and metadata generation."""
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
    X_train = train_df[SENSOR_FEATURES]
    y_train = train_df[TARGET_COLUMN].astype(int)

    model, metadata = train_and_save_final_model(X_train, y_train)

    assert MODEL_FILE.exists()
    assert METADATA_FILE.exists()

    # Verify model loading
    loaded_model = load_model(MODEL_FILE)
    preds = loaded_model.predict(X_train[SENSOR_FEATURES])
    assert len(preds) == len(X_train)
    assert set(preds).issubset({0, 1, 2})

    # Verify probability predictions
    probs = loaded_model.predict_proba(X_train[SENSOR_FEATURES])
    assert probs.shape == (len(X_train), 3)
    assert np.allclose(probs.sum(axis=1), 1.0)

    # Verify metadata fields
    loaded_meta = load_metadata(METADATA_FILE)
    assert loaded_meta["model_name"] == "RandomForestClassifier"
    assert loaded_meta["dataset_type"] == "synthetic"
    assert loaded_meta["feature_names"] == SENSOR_FEATURES
    assert "feature_importances" in loaded_meta
    assert len(loaded_meta["feature_importances"]) == 5


if __name__ == "__main__":
    test_candidate_models_dict()
    test_benchmark_candidate_models()
    test_train_and_save_final_model()
    print("All Stage 6 model training tests passed successfully!")
