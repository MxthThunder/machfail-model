"""Stage 8 Machine Health Score Unit Tests."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.health_score import calculate_health_score, compute_sensor_strain_penalty


def test_health_score_normal_condition():
    """Verify clean nominal readings yield 90-100 score."""
    normal_probs = {"NORMAL": 0.98, "WARNING": 0.02, "FAULT": 0.0}
    res = calculate_health_score(
        rpm=1505.0,
        temperature=31.5,
        humidity=59.0,
        current=0.71,
        vibration=0.095,
        probabilities=normal_probs,
    )
    assert 90 <= res.health_score <= 100, f"Expected normal score 90-100, got {res.health_score}"
    assert res.health_category == "NORMAL"
    assert res.status_code == 0
    assert "within nominal baseline limits" in res.contributing_factors[0]


def test_health_score_warning_condition():
    """Verify elevated temperature/current/vibration yields 70-89 score."""
    warning_probs = {"NORMAL": 0.10, "WARNING": 0.85, "FAULT": 0.05}
    res = calculate_health_score(
        rpm=1380.0,
        temperature=42.0,
        humidity=62.0,
        current=0.96,
        vibration=0.28,
        probabilities=warning_probs,
    )
    assert 70 <= res.health_score <= 89, f"Expected warning score 70-89, got {res.health_score}"
    assert res.health_category == "WARNING"
    assert res.status_code == 1
    assert len(res.contributing_factors) >= 1


def test_health_score_fault_condition():
    """Verify critical thermal/current overload yields 0-69 score."""
    fault_probs = {"NORMAL": 0.0, "WARNING": 0.08, "FAULT": 0.92}
    res = calculate_health_score(
        rpm=950.0,
        temperature=58.0,
        humidity=65.0,
        current=1.55,
        vibration=0.62,
        probabilities=fault_probs,
    )
    assert 0 <= res.health_score <= 69, f"Expected fault score 0-69, got {res.health_score}"
    assert res.health_category == "FAULT"
    assert res.status_code == 2
    assert any("Critical thermal" in f or "severe overload" in f for f in res.contributing_factors)


def test_health_score_boundary_clamping():
    """Verify health score is always clamped within [0, 100]."""
    # Absolute worst case
    worst_probs = {"NORMAL": 0.0, "WARNING": 0.0, "FAULT": 1.0}
    res_min = calculate_health_score(
        rpm=0.0,
        temperature=100.0,
        humidity=100.0,
        current=10.0,
        vibration=5.0,
        probabilities=worst_probs,
    )
    assert res_min.health_score == 0

    # Ideal best case
    best_probs = {"NORMAL": 1.0, "WARNING": 0.0, "FAULT": 0.0}
    res_max = calculate_health_score(
        rpm=1500.0,
        temperature=30.0,
        humidity=50.0,
        current=0.70,
        vibration=0.08,
        probabilities=best_probs,
    )
    assert res_max.health_score == 100


if __name__ == "__main__":
    test_health_score_normal_condition()
    test_health_score_warning_condition()
    test_health_score_fault_condition()
    test_health_score_boundary_clamping()
    print("All Stage 8 health score tests passed successfully!")
