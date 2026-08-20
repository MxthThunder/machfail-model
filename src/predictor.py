"""Prediction and Diagnostic Explanation Engine for Industrial Machine AI Subsystem.

Provides high-level inference wrapping the trained RandomForestClassifier,
confidence estimation, health score derivation, and uncertainty-aware explanations.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    MODEL_FILE,
    METADATA_FILE,
    SENSOR_FEATURES,
    STATUS_MAP,
)
from src.train import load_model, load_metadata
from src.health_score import calculate_health_score


class MachinePredictor:
    """Singleton predictor holding trained model and metadata."""

    _instance: Optional["MachinePredictor"] = None

    def __init__(self, model_path: Path = MODEL_FILE, metadata_path: Path = METADATA_FILE):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = load_model(self.model_path)
        self.metadata = load_metadata(self.metadata_path)

    @classmethod
    def get_instance(cls) -> "MachinePredictor":
        """Returns or initializes the singleton predictor instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(
        self,
        rpm: float,
        temperature: float,
        humidity: float,
        current: float,
        vibration: float,
    ) -> Dict[str, Any]:
        """Performs end-to-end inference on incoming sensor readings.

        Parameters
        ----------
        rpm : float
            Motor rotational speed in RPM.
        temperature : float
            Motor/ambient temperature in deg C.
        humidity : float
            Ambient relative humidity in %.
        current : float
            Motor current draw in Amperes.
        vibration : float
            Mechanical vibration intensity in g.

        Returns
        -------
        Dict[str, Any]
            Comprehensive prediction dictionary including status, health score,
            confidence, and diagnostic explanation.
        """
        # Create input row strictly matching SENSOR_FEATURES order
        input_data = pd.DataFrame(
            [
                {
                    "rpm": float(rpm),
                    "temperature": float(temperature),
                    "humidity": float(humidity),
                    "current": float(current),
                    "vibration": float(vibration),
                }
            ],
            columns=SENSOR_FEATURES,
        )

        # 1. Model Inference (Probabilities & Class)
        probs_array = self.model.predict_proba(input_data[SENSOR_FEATURES])[0]
        pred_class_idx = int(np.argmax(probs_array))
        confidence = float(np.max(probs_array))
        status_name = STATUS_MAP.get(pred_class_idx, "UNKNOWN")

        prob_dict = {
            "NORMAL": round(float(probs_array[0]), 4),
            "WARNING": round(float(probs_array[1]), 4),
            "FAULT": round(float(probs_array[2]), 4),
        }

        # 2. Derive Machine Health Score and Contributing Factors
        health_result = calculate_health_score(
            rpm=rpm,
            temperature=temperature,
            humidity=humidity,
            current=current,
            vibration=vibration,
            probabilities=prob_dict,
        )

        # 3. Uncertainty-Aware Diagnostic Explanation
        if pred_class_idx == 0:
            prediction_text = (
                "Nominal operating conditions with stable sensor telemetry and smooth mechanical behavior."
            )
        elif pred_class_idx == 1:
            prediction_text = (
                "Sensor pattern is consistent with possible motor overload, elevated thermal stress, or developing friction."
            )
        else:
            prediction_text = (
                "Critical sensor pattern consistent with impending mechanical seizure, severe electrical overload, or bearing breakdown."
            )

        return {
            "status": status_name,
            "status_code": pred_class_idx,
            "health_score": health_result.health_score,
            "health_category": health_result.health_category,
            "confidence": round(confidence, 4),
            "prediction": prediction_text,
            "probabilities": prob_dict,
            "contributing_factors": health_result.contributing_factors,
            "timestamp": datetime.now().isoformat(),
            "model_version": self.metadata.get("model_version", "1.0.0"),
        }


def predict_machine_status(
    rpm: float,
    temperature: float,
    humidity: float,
    current: float,
    vibration: float,
) -> Dict[str, Any]:
    """Convenience functional interface for machine status prediction."""
    predictor = MachinePredictor.get_instance()
    return predictor.predict(
        rpm=rpm,
        temperature=temperature,
        humidity=humidity,
        current=current,
        vibration=vibration,
    )


if __name__ == "__main__":
    import json

    print("Running Sample Inference via predictor.py...")
    sample_res = predict_machine_status(
        rpm=1380.0,
        temperature=42.5,
        humidity=62.0,
        current=0.98,
        vibration=0.28,
    )
    print(json.dumps(sample_res, indent=4))
