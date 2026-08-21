"""Script to send sample or streaming ESP32 telemetry JSON to backend for testing."""

import sys
import time
import argparse
import requests

DEFAULT_URL = "http://localhost:8000/api/motor/data"


def generate_sample_reading(motor_id: str = "M001", status: str = "ON", iteration: int = 0) -> dict:
    """Generates a realistic telemetry payload mimicking the real ESP32 sensors."""
    # Temperature: DHT22 range ~40-45 C under load
    temp = 42.0 + (iteration % 5) * 0.3
    humidity = 62.0 - (iteration % 4) * 0.2
    
    # ACS712: 5A version (~1850 ADC, ~2.40A when ON, 0A when OFF)
    current = 2.40 if status == "ON" else 0.0
    acs_adc = 1850.0 if status == "ON" else 0.0
    
    # MPU6050: Acceleration in g
    mpu_x = 0.259
    mpu_y = -0.965
    mpu_z = -0.062
    total_accel = 1.021
    vibration = abs(total_accel - 1.0)  # 0.021
    vibration_level = "LOW"
    
    return {
        "motor_id": motor_id,
        "status": status,
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2),
        "ir": 1 if status == "ON" else 0,
        "acs_adc": acs_adc,
        "current": round(current, 2),
        "mpu_x": mpu_x,
        "mpu_y": mpu_y,
        "mpu_z": mpu_z,
        "total_acceleration": round(total_accel, 3),
        "vibration": round(vibration, 3),
        "vibration_level": vibration_level,
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
