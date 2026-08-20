"""Machine Health Score Engine for Industrial Machine AI Subsystem.

Calculates an explainable AI-derived Machine Health Score (0 - 100) combining
model prediction probabilities and sensor operational strain indices.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import HEALTH_SCORE_THRESHOLDS, STATUS_MAP


# Engineering Baseline Reference Points (Small DC Motor Bench)
NOMINAL_BASELINES = {
    "rpm": 1500.0,          # Nominal operating speed (RPM)
    "temperature": 32.0,    # Nominal steady-state temp (°C)
    "current": 0.72,        # Nominal current draw (A)
    "vibration": 0.10,      # Smooth baseline vibration (g)
}

# Warning / Critical Sensor Thresholds for contributing factor diagnostics
DIAGNOSTIC_THRESHOLDS = {
    "rpm": {"warning_min": 1420.0, "fault_min": 1250.0, "unit": "RPM"},
    "temperature": {"warning_max": 38.0, "fault_max": 48.0, "unit": "°C"},
    "current": {"warning_max": 0.85, "fault_max": 1.20, "unit": "A"},
    "vibration": {"warning_max": 0.20, "fault_max": 0.40, "unit": "g"},
}


@dataclass
class HealthScoreResult:
    """Structured result containing health score, category, and diagnostic factors."""

    health_score: int
    health_category: str
    status_code: int
    probabilities: Dict[str, float]
    contributing_factors: List[str]
    score_breakdown: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health_score": self.health_score,
            "health_category": self.health_category,
            "status_code": self.status_code,
            "probabilities": self.probabilities,
            "contributing_factors": self.contributing_factors,
            "score_breakdown": self.score_breakdown,
        }
def compute_sensor_strain_penalty(
    rpm: float,
    temperature: float,
    current: float,
    vibration: float,
) -> Tuple[float, List[str]]:
    """Calculates operational strain penalty points (0 - 10) and identifies contributing factors."""
    penalty = 0.0
    factors = []

    # 1. Temperature Strain
    temp_thresh = DIAGNOSTIC_THRESHOLDS["temperature"]
    if temperature >= temp_thresh["fault_max"]:
        penalty += 4.0
        factors.append(
            f"Critical thermal buildup ({temperature:.1f} C) exceeds safe fault limit ({temp_thresh['fault_max']} C)."
        )
    elif temperature >= temp_thresh["warning_max"]:
        penalty += 1.5
        factors.append(
            f"Elevated temperature ({temperature:.1f} C) exceeds nominal baseline ({NOMINAL_BASELINES['temperature']} C)."
        )

    # 2. Current Draw Strain
    curr_thresh = DIAGNOSTIC_THRESHOLDS["current"]
    if current >= curr_thresh["fault_max"]:
        penalty += 3.0
        factors.append(
            f"High motor current draw ({current:.2f} A) indicates severe overload or mechanical binding."
        )
    elif current >= curr_thresh["warning_max"]:
        penalty += 1.5
        factors.append(
            f"Increased current draw ({current:.2f} A) above nominal ({NOMINAL_BASELINES['current']} A)."
        )

    # 3. Vibration Strain
    vib_thresh = DIAGNOSTIC_THRESHOLDS["vibration"]
    if vibration >= vib_thresh["fault_max"]:
        penalty += 3.0
        factors.append(
            f"Severe mechanical vibration ({vibration:.3f} g) detected, indicating eccentricity or bearing wear."
        )
    elif vibration >= vib_thresh["warning_max"]:
        penalty += 1.5
        factors.append(
            f"Elevated vibration ({vibration:.3f} g) higher than nominal smooth baseline ({NOMINAL_BASELINES['vibration']} g)."
        )

    # 4. RPM Speed Sag
    rpm_thresh = DIAGNOSTIC_THRESHOLDS["rpm"]
    if rpm <= rpm_thresh["fault_min"]:
        penalty += 3.0
        factors.append(
            f"Significant RPM drop ({rpm:.0f} RPM) below fault limit ({rpm_thresh['fault_min']} RPM)."
        )
    elif rpm <= rpm_thresh["warning_min"]:
        penalty += 1.5
        factors.append(
            f"Moderate RPM speed sag ({rpm:.0f} RPM) compared to nominal speed ({NOMINAL_BASELINES['rpm']} RPM)."
        )

    if not factors:
        factors.append("All sensor channels operating within nominal baseline limits.")

    # Cap physical penalty to max 10 points
    penalty = min(10.0, penalty)
    return penalty, factors


def calculate_health_score(
    rpm: float,
    temperature: float,
    humidity: float,
    current: float,
    vibration: float,
    probabilities: Dict[str, float] | np.ndarray,
) -> HealthScoreResult:
    """Computes the 0-100 Machine Health Score using ML probabilities and sensor strain indices.

    Calculation Strategy:
    1. Base Probabilistic Score (0 - 100):
       Base = (1.00 * P_normal + 0.82 * P_warning + 0.15 * P_fault) * 100
    2. Physical Sensor Strain Penalty (0 - 10 points deducted for sensor excursions).
    3. Clamping between 0 and 100.
    """
    # Normalize probabilities input
    if isinstance(probabilities, np.ndarray):
        p_normal = float(probabilities[0])
        p_warning = float(probabilities[1])
        p_fault = float(probabilities[2])
    elif isinstance(probabilities, dict):
        p_normal = float(probabilities.get("NORMAL", probabilities.get(0, 0.0)))
        p_warning = float(probabilities.get("WARNING", probabilities.get(1, 0.0)))
        p_fault = float(probabilities.get("FAULT", probabilities.get(2, 0.0)))
    else:
        raise TypeError("Probabilities must be a dict or numpy array")

    prob_dict = {
        "NORMAL": round(p_normal, 4),
        "WARNING": round(p_warning, 4),
        "FAULT": round(p_fault, 4),
    }

    # Step 1: Base Probabilistic Score
    base_score = (1.00 * p_normal + 0.80 * p_warning + 0.00 * p_fault) * 100.0

    # Step 2: Physical Strain Penalty
    strain_penalty, contributing_factors = compute_sensor_strain_penalty(
        rpm=rpm,
        temperature=temperature,
        current=current,
        vibration=vibration,
    )

    # Step 3: Final Score Clamping
    raw_final_score = base_score - strain_penalty
    final_score = int(round(np.clip(raw_final_score, 0, 100)))

    # Determine health category based on standard thresholds
    if final_score >= 90:
        health_category = "NORMAL"
        status_code = 0
    elif final_score >= 70:
        health_category = "WARNING"
        status_code = 1
    else:
        health_category = "FAULT"
        status_code = 2

    breakdown = {
        "base_probabilistic_score": round(base_score, 1),
        "sensor_strain_penalty": round(strain_penalty, 1),
        "final_clamped_score": final_score,
        "calculation_formula": "Final Score = clamp(round(100*P_norm + 75*P_warn + 0*P_fault - StrainPenalty), 0, 100)",
        "provenance_note": "AI-derived machine health score for student demonstrator setup.",
    }

    return HealthScoreResult(
        health_score=final_score,
        health_category=health_category,
        status_code=status_code,
        probabilities=prob_dict,
        contributing_factors=contributing_factors,
        score_breakdown=breakdown,
    )


def main():
    parser = argparse.ArgumentParser(description="Calculate machine health score from sensor telemetry.")
    parser.add_argument("--rpm", type=float, default=1380.0)
    parser.add_argument("--temp", type=float, default=42.5)
    parser.add_argument("--humidity", type=float, default=62.0)
    parser.add_argument("--current", type=float, default=0.98)
    parser.add_argument("--vibration", type=float, default=0.28)
    args = parser.parse_args()

    # Demonstration with simulated warning probabilities
    demo_probs = {"NORMAL": 0.15, "WARNING": 0.82, "FAULT": 0.03}
    result = calculate_health_score(
        rpm=args.rpm,
        temperature=args.temp,
        humidity=args.humidity,
        current=args.current,
        vibration=args.vibration,
        probabilities=demo_probs,
    )

    print("=" * 60)
    print(" MACHINE HEALTH SCORE DIAGNOSTIC OUTPUT")
    print("=" * 60)
    print(f"Health Score     : {result.health_score} / 100")
    print(f"Health Category  : {result.health_category}")
    print(f"Status Code      : {result.status_code}")
    print(f"Model Probs      : {result.probabilities}")
    print("\nContributing Diagnostic Factors:")
    for f in result.contributing_factors:
        print(f"  - {f}")
    print("\nScore Calculation Breakdown:")
    for k, v in result.score_breakdown.items():
        print(f"  - {k:26s}: {v}")
    print("=" * 60)


if __name__ == "__main__":
    main()
