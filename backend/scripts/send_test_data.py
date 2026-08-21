"""Script to send sample or streaming ESP32 telemetry JSON to backend for testing."""

import sys
import time
import argparse
import requests

DEFAULT_URL = "http://localhost:8000/api/motor/data"


def generate_sample_reading(motor_id: str = "M001", status: str = "ON", iteration: int = 0) -> dict:
    """
    Generates a development test telemetry payload matching the real ESP32 JSON schema.
    NOTE: For development/testing only; does not replace real ESP32 hardware streaming.
    """
    temp = 33.9 + (iteration % 5) * 0.2
    humidity = 69.0 - (iteration % 4) * 0.1
    current = 0.08 if status == "ON" else 0.0
    acs_adc = 530.0 if status == "ON" else 0.0
    ir_pulses = 5516 + iteration * 25
    rpm = 2945.7 if status == "ON" else 0.0
    motor_pwm = 255 if status == "ON" else 0
    
    mpu_x = 0.01
    mpu_y = 0.09
    mpu_z = -0.46
    total_accel = 0.47
    vibration = 0.53
    vibration_level = "HIGH"
    
    return {
        "motor_id": motor_id,
        "status": status,
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2),
        "ir": 0 if status == "ON" else 1,
        "ir_pulses": ir_pulses,
        "rpm": round(rpm, 1),
        "acs_adc": acs_adc,
        "current": round(current, 2),
        "mpu_x": mpu_x,
        "mpu_y": mpu_y,
        "mpu_z": mpu_z,
        "total_acceleration": round(total_accel, 3),
        "vibration": round(vibration, 3),
        "vibration_level": vibration_level,
        "motor_pwm": motor_pwm,
        "voltage": None,
        "esp32_ip": "192.168.1.150"
    }


def send_data(endpoint_url: str, payload: dict):
    """Sends a single POST request to the backend API."""
    try:
        res = requests.post(endpoint_url, json=payload, timeout=5)
        print(f"[{res.status_code}] Response: {res.json()}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to {endpoint_url}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Send test ESP32 telemetry JSON to backend")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"Backend endpoint URL (default: {DEFAULT_URL})")
    parser.add_argument("--motor-id", default="M001", help="Motor ID (default: M001)")
    parser.add_argument("--status", default="ON", choices=["ON", "OFF"], help="Motor status (default: ON)")
    parser.add_argument("--stream", action="store_true", help="Send streaming data continuously")
    parser.add_argument("--interval", type=float, default=2.0, help="Stream interval in seconds (default: 2.0)")
    parser.add_argument("--count", type=int, default=1, help="Number of packets to send if not streaming (default: 1)")

    args = parser.parse_args()

    print(f"Target URL: {args.url}")
    print(f"Motor ID:   {args.motor_id}")
    print(f"Status:     {args.status}")
    print("-" * 50)

    if args.stream:
        print("Starting live telemetry stream (Press Ctrl+C to stop)...")
        iteration = 0
        try:
            while True:
                payload = generate_sample_reading(args.motor_id, args.status, iteration)
                print(f"[{time.strftime('%X')}] Sending packet #{iteration + 1}...")
                send_data(args.url, payload)
                iteration += 1
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStreaming stopped.")
    else:
        for i in range(args.count):
            payload = generate_sample_reading(args.motor_id, args.status, i)
            send_data(args.url, payload)
            if i < args.count - 1:
                time.sleep(args.interval)


if __name__ == "__main__":
    main()
