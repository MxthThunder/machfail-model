# ESP32 Motor Monitoring System - Backend

Production-ready FastAPI backend for receiving real-time live telemetry from an ESP32 motor monitoring unit, storing time-series records in SQLite, tracking motor online status and runtime, queueing motor commands, and broadcasting live sensor streams via WebSockets.

---

## 1. Prerequisites & Python Version
- **Python Version**: `Python 3.10` or higher (tested with `Python 3.13`)
- **Operating System**: Windows, macOS, or Linux

---

## 2. Virtual Environment Setup

### Windows (PowerShell / Command Prompt)
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the Backend Server

To make the server reachable by external hardware devices on your local Wi-Fi network (such as the ESP32), bind to `0.0.0.0`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 5. Finding Your Computer's Local IP Address

The ESP32 is a separate physical device on your Wi-Fi network. It **cannot** connect to `127.0.0.1` or `localhost` (which would refer to the ESP32 itself).

### Windows
1. Open PowerShell / Command Prompt.
2. Run:
   ```cmd
   ipconfig
   ```
3. Look for your active Wi-Fi adapter (e.g., `IPv4 Address . . . . . . . . . . . : 192.168.1.100`).

### Linux / macOS
```bash
hostname -I
# or
ip addr show
# or (macOS)
ipconfig getifaddr en0
```

> **IMPORTANT**: If your PC IP is `192.168.1.100`, the ESP32 must send requests to:  
> `http://192.168.1.100:8000/api/motor/data`

---

## 6. API Reference

### Health Check
- **`GET /api/health`**  
  Returns system readiness status.

### Telemetry Ingestion (ESP32 -> Backend)
- **`POST /api/motor/data`**  
  Accepts live sensor payload from the ESP32.
  - Validates payload with Pydantic.
  - Persists record into SQLite database (`motor_monitoring.db`).
  - Calculates accumulated motor operational runtime.
  - Updates latest motor cache and online state.
  - Broadcasts live telemetry packet to WebSocket subscribers on `/ws/motor/{motor_id}`.

  **Request Payload Example:**
  ```json
  {
    "motor_id": "M001",
    "status": "ON",
    "temperature": 42.5,
    "humidity": 62.2,
    "ir": 1,
    "acs_adc": 1850,
    "current": 2.40,
    "mpu_x": 0.259,
    "mpu_y": -0.965,
    "mpu_z": -0.062,
    "total_acceleration": 1.021,
    "vibration": 0.021,
    "vibration_level": "LOW"
  }
  ```

  **Response (201 Created):**
  ```json
  {
    "success": true,
    "message": "Motor data received",
    "motor_id": "M001",
    "timestamp": "2026-08-21T20:31:36.123456Z"
  }
  ```

### Latest Telemetry
- **`GET /api/motor/latest?motor_id=M001`**  
  Returns the most recently received real sensor reading for the motor.

  **Response (200 OK):**
  ```json
  {
    "motor_id": "M001",
    "status": "ON",
    "temperature": 42.5,
    "humidity": 62.2,
    "ir": 1,
    "acs_adc": 1850,
    "current": 2.40,
    "mpu_x": 0.259,
    "mpu_y": -0.965,
    "mpu_z": -0.062,
    "total_acceleration": 1.021,
    "vibration": 0.021,
    "vibration_level": "LOW",
    "voltage": null,
    "esp32_ip": "192.168.1.150",
    "received_at": "2026-08-21T20:31:36.123456Z"
  }
  ```

### Motor Online Status & Runtime
- **`GET /api/motor/status?motor_id=M001`**  
  Determines whether the ESP32 is currently online based on a 10-second activity window and returns accumulated runtime.

  **Response (200 OK):**
  ```json
  {
    "motor_id": "M001",
    "status": "ON",
    "online": true,
    "last_seen": "2026-08-21T20:31:36.123456Z",
    "runtime_seconds": 184.2
  }
  ```

### Historical Data
- **`GET /api/motor/history/M001?limit=50`**  
  Returns up to `limit` historical telemetry records in reverse chronological order.

### Motor Control & Polling
- **`POST /api/motor/control`**  
  Queues a control command without claiming premature state transition.
  ```json
  {
    "motor_id": "M001",
    "command": "ON"
  }
  ```
  **Response:**
  ```json
  {
    "motor_id": "M001",
    "requested_command": "ON",
    "actual_status": "OFF",
    "command_status": "PENDING",
    "command_id": "cmd_a1b2c3d4e5f6"
  }
  ```

- **`GET /api/motor/command/M001`**  
  Polled by ESP32 to retrieve pending commands.
  ```json
  {
    "motor_id": "M001",
    "command": "ON",
    "command_id": "cmd_a1b2c3d4e5f6",
    "has_pending_command": true,
    "created_at": "2026-08-21T20:31:36.123456Z"
  }
  ```

- **`POST /api/motor/command/ack`**  
  Sent by ESP32 to acknowledge command execution.
  ```json
  {
    "motor_id": "M001",
    "command_id": "cmd_a1b2c3d4e5f6",
    "status": "EXECUTED"
  }
  ```

### Real-Time WebSocket
- **`ws://localhost:8000/ws/motor/M001`**  
  Subscribes to live sensor packets pushed upon every incoming ESP32 transmission.

---

## 7. Interactive API Documentation (Swagger)

Open your browser and navigate to:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 8. Automated Testing

Run the full pytest suite:
```bash
python -m pytest tests/test_api.py -v
```

Run test client script to simulate telemetry when ESP32 is not plugged in:
```bash
# Send a single test packet:
python scripts/send_test_data.py --status ON

# Send a continuous 2-second stream:
python scripts/send_test_data.py --stream --interval 2.0
```

---

## 9. Future Integration Points

### Frontend (React / Vite)
- Connect REST calls to `http://localhost:8000/api/motor/*`
- Connect WebSocket for live charts to `ws://localhost:8000/ws/motor/M001`
- CORS is enabled by default to allow seamless local development.

### Machine Learning Predictive Maintenance
- The boundary interface is configured at `app/services/ml_service.py`.
- Accepts features: `temperature`, `humidity`, `current`, `voltage` (optional), `mpu_x`, `mpu_y`, `mpu_z`, `total_acceleration`, `vibration`, and `motor_runtime_seconds`.
