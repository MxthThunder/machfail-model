"""Motor Condition Analysis & Rule-Based Predictive Maintenance Engine.

Evaluates four physical telemetry parameters:
1. Temperature (°C)
2. RPM
3. Current (A)
4. Vibration (g)

Classifies each parameter into NORMAL / MEDIUM / HIGH, computes condition score (0-8),
evaluates overall condition with strict priority (HIGH > MEDIUM > NORMAL),
generates clear failure/warning explanations, and assesses Rule-Based Failure Risk.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.models import utc_now


def classify_temperature(temp: float) -> Dict[str, Any]:
    """
    Temperature Rules:
    30 <= temperature < 35  = NORMAL (score 0)
    35 <= temperature < 40  = MEDIUM (score 1)
    40 <= temperature <= 45 = HIGH (score 2)
    Outside 30-45°C         = OUT_OF_RANGE
    """
    if 30.0 <= temp < 35.0:
        return {"condition": "NORMAL", "score": 0, "desc": None}
    elif 35.0 <= temp < 40.0:
        return {"condition": "MEDIUM", "score": 1, "desc": "Elevated temperature detected"}
    elif 40.0 <= temp <= 45.0:
        return {"condition": "HIGH", "score": 2, "desc": "High temperature detected"}
    elif temp > 45.0:
        return {"condition": "HIGH", "score": 2, "desc": "Critical high temperature detected"}
    else:  # temp < 30.0
        return {"condition": "NORMAL", "score": 0, "desc": None}


def classify_rpm(rpm: float) -> Dict[str, Any]:
    """
    RPM Rules:
    rpm > 1000          = NORMAL (score 0)
    500 <= rpm <= 1000  = MEDIUM (score 1, exactly 1000 is MEDIUM)
    rpm < 500           = HIGH (score 2, low RPM indicates stall/load sag)
    """
    if rpm > 1000.0:
        return {"condition": "NORMAL", "score": 0, "desc": None}
    elif 500.0 <= rpm <= 1000.0:
        return {"condition": "MEDIUM", "score": 1, "desc": "Moderate RPM detected"}
    else:
        return {"condition": "HIGH", "score": 2, "desc": "Low RPM detected"}


def classify_current(current: float) -> Dict[str, Any]:
    """
    Current Rules:
    current < 1.0        = NORMAL (score 0)
    1.0 <= current < 1.5 = MEDIUM (score 1, exactly 1.0 is MEDIUM)
    1.5 <= current       = HIGH (score 2, exactly 1.5 is HIGH)
    """
    if current < 1.0:
        return {"condition": "NORMAL", "score": 0, "desc": None}
    elif 1.0 <= current < 1.5:
        return {"condition": "MEDIUM", "score": 1, "desc": "Elevated motor current detected"}
    else:
        return {"condition": "HIGH", "score": 2, "desc": "High motor current detected"}


def classify_vibration(vibration: float) -> Dict[str, Any]:
    """
    Vibration Rules:
    vibration <= 2000          = NORMAL (score 0)
    2000 < vibration <= 3000   = MEDIUM (score 1)
    vibration > 3000           = HIGH (score 2)
    """
    if vibration <= 2000.0:
        return {"condition": "NORMAL", "score": 0, "desc": None}
    elif 2000.0 < vibration <= 3000.0:
        return {"condition": "MEDIUM", "score": 1, "desc": "Elevated vibration detected"}
    else:
        return {"condition": "HIGH", "score": 2, "desc": "High vibration detected"}


class ConditionAnalysisService:
    """Intelligent rule-based motor condition and failure risk evaluation service."""

    def evaluate_condition(
        self,
        motor_id: str,
        temperature: float,
        rpm: float,
        current: float,
        vibration: float,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates physical parameters and produces comprehensive condition report.
        """
        temp_res = classify_temperature(temperature)
        rpm_res = classify_rpm(rpm)
        current_res = classify_current(current)
        vibe_res = classify_vibration(vibration)

        conditions = [
            temp_res["condition"],
            rpm_res["condition"],
            current_res["condition"],
            vibe_res["condition"],
        ]

        # Overall Condition Priority Rule: HIGH > MEDIUM > NORMAL
        if "HIGH" in conditions:
            overall_condition = "HIGH"
            failure_risk = "HIGH"
        elif "MEDIUM" in conditions:
            overall_condition = "MEDIUM"
            failure_risk = "MEDIUM"
        else:
            overall_condition = "NORMAL"
            failure_risk = "LOW"

        # Condition Score Calculation
        temp_score = temp_res["score"]
        rpm_score = rpm_res["score"]
        current_score = current_res["score"]
        vibe_score = vibe_res["score"]

        total_score = temp_score + rpm_score + current_score + vibe_score
        max_score = 8

        # Generate Failure / Warning Explanation Messages
        descriptions: List[str] = []
        for res in [temp_res, rpm_res, current_res, vibe_res]:
            if res["desc"]:
                descriptions.append(res["desc"])

        if not descriptions:
            message = "Motor operating normally"
        elif len(descriptions) == 1:
            message = descriptions[0]
        elif len(descriptions) == 2:
            # Lowercase the second message start for natural grammar
            d1, d2 = descriptions[0], descriptions[1]
            d2_lower = d2[0].lower() + d2[1:] if d2 else ""
            message = f"{d1} and {d2_lower}"
        else:
            message = "; ".join(descriptions)

        ts = timestamp if timestamp else utc_now().isoformat()

        return {
            "motor_id": motor_id,
            "temperature": {
                "value": float(temperature),
                "unit": "°C",
                "condition": temp_res["condition"],
                "score": temp_score,
            },
            "rpm": {
                "value": float(rpm),
                "unit": "RPM",
                "condition": rpm_res["condition"],
                "score": rpm_score,
            },
            "current": {
                "value": float(current),
                "unit": "A",
                "condition": current_res["condition"],
                "score": current_score,
            },
            "vibration": {
                "value": float(vibration),
                "unit": "g",
                "condition": vibe_res["condition"],
                "score": vibe_score,
            },
            "overall_condition": overall_condition,
            "condition_score": total_score,
            "maximum_score": max_score,
            "failure_risk": failure_risk,
            "risk_type": "Rule-Based Failure Risk",
            "stages": {
                "sensor_data_analysis": "Complete",
                "motor_condition_prediction": "Complete",
                "failure_risk_analysis": "Complete",
            },
            "message": message,
            "timestamp": ts,
        }


condition_service = ConditionAnalysisService()
