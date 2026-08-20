"""ESP32 Telemetry Streaming Simulator for Predictive Maintenance AI.

Simulates Person 1's ESP32 microcontroller reading physical sensors and transmitting
live JSON telemetry over HTTP POST to the AI Prediction API at regular intervals.
"""

import argparse
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Standard default endpoint
DEFAULT_API_URL = "http://127.0.0.1:8000/predict"


def get_demo_telemetry_sequence(count: int = 12) -> List[Dict[str, float]]:
    """Generates a realistic sequence demonstrating Normal -> Warning -> Fault -> Recovery."""
    sequence = []

    # Phase 1: Normal Operation (Ticks 0 - 3)
    for _ in range(4):
        sequence.append({
            "rpm": 1502.0,
            "temperature": 32.1,
            "humidity": 59.0,
            "current": 0.72,
            "vibration": 0.095,
        })

    # Phase 2: Warning - Mechanical Friction & Heat Build-up (Ticks 4 - 7)
    for i in range(4):
        sequence.append({
            "rpm": round(1410.0 - i * 15, 1),
            "temperature": round(39.0 + i * 2.0, 1),
            "humidity": 61.5,
            "current": round(0.88 + i * 0.05, 2),
            "vibration": round(0.22 + i * 0.03, 3),
        })

    # Phase 3: Fault - Severe Overload / Impending Seizure (Ticks 8 - 10)
    for i in range(3):
        sequence.append({
            "rpm": round(980.0 - i * 60, 1),
            "temperature": round(54.0 + i * 3.5, 1),
            "humidity": 64.0,
            "current": round(1.45 + i * 0.10, 2),
            "vibration": round(0.55 + i * 0.06, 3),
        })

    # Phase 4: Recovery / Cooldown after technician intervention (Tick 11+)
    sequence.append({
        "rpm": 1495.0,
        "temperature": 34.0,
        "humidity": 59.5,
        "current": 0.73,
        "vibration": 0.105,
    })

    return sequence[:count]


def transmit_reading(url: str, payload: Dict[str, float]) -> Dict[str, Any]:
    """Transmits a single telemetry payload over HTTP POST to the AI API."""
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start_time = time.perf_counter()
    with urllib.request.urlopen(req, timeout=5.0) as response:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        resp_data = json.loads(response.read().decode("utf-8"))
        resp_data["_latency_ms"] = round(latency_ms, 2)
        return resp_data


def run_stream(url: str, count: int, interval: float):
    """Streams a sequence of telemetry readings to the API server."""
    sequence = get_demo_telemetry_sequence(count)

    print("=" * 80)
    print(" ESP32 TELEMETRY TRANSMITTER SIMULATOR (Person 1 -> Person 3 AI API)")
    print("=" * 80)
    print(f"Target URL       : {url}")
    print(f"Transmission Rate: 1 packet every {interval} second(s)")
    print(f"Total Packets    : {len(sequence)}")
    print("-" * 80)
    print(f"{'Time':8s} | {'RPM':>6s} {'Temp':>6s} {'Curr':>6s} {'Vib':>6s} -> {'STATUS':8s} {'Score':>5s} {'Conf':>6s} {'Latency':>8s}")
    print("-" * 80)

    for idx, reading in enumerate(sequence):
        t_str = datetime.now().strftime("%H:%M:%S")
        try:
            res = transmit_reading(url, reading)
            status_tag = res.get("status", "UNKNOWN")
            score = res.get("health_score", 0)
            conf = res.get("confidence", 0.0) * 100
            latency = res.get("_latency_ms", 0.0)

            print(
                f"[{t_str}] | {reading['rpm']:6.0f} {reading['temperature']:5.1f}C {reading['current']:5.2f}A {reading['vibration']:5.3f}g -> "
                f"{status_tag:8s} {score:4d}/100 {conf:5.1f}% {latency:6.1f}ms"
            )

        except urllib.error.URLError as e:
            print(f"[{t_str}] | Transmission FAILED: {e.reason}")
            print("\n[HINT] Ensure the FastAPI server is running: `uvicorn src.api:app --reload`")
            break
        except Exception as e:
            print(f"[{t_str}] | Error: {e}")
            break

        if idx < len(sequence) - 1:
            time.sleep(interval)

    print("=" * 80)
    print("ESP32 telemetry transmission completed.")


def main():
    parser = argparse.ArgumentParser(description="Simulate live ESP32 sensor telemetry stream.")
    parser.add_argument("--url", type=str, default=DEFAULT_API_URL, help=f"AI Prediction API endpoint (default: {DEFAULT_API_URL})")
    parser.add_argument("--count", type=int, default=12, help="Number of telemetry packets to send (default: 12)")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between packets in seconds (default: 1.0)")
    args = parser.parse_args()

    run_stream(url=args.url, count=args.count, interval=args.interval)


if __name__ == "__main__":
    main()
