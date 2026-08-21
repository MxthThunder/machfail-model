# ⚙️ IoT Motor Monitoring & Predictive Maintenance System

An industrial-grade IoT telemetry, actuation, condition analysis, and rule-based predictive maintenance platform for electric motors.

---

## 🌟 System Architecture

```
                                 [ REAL MOTOR & SENSORS ]
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             │  • DHT22: Temperature (°C), Humidity (%)                      │
             │  • Optical IR Sensor: State (0/1), IR Pulses, RPM             │
             │  • ACS712: Current Draw (Amperes), Raw ADC Count              │
             │  • MPU6050: 3-Axis Accel (g), Total Accel (g), Vibration (g)  │
             │  • L298N: Driver Status (ON/OFF), PWM Duty (0-255)            │
             └───────────────────────────────┬───────────────────────────────┘
                                             ▼
                                     [ ESP32 FIRMWARE ]
                                             │  (Wi-Fi JSON POST)
                                             ▼
                               [ FASTAPI BACKEND SERVER ]
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
             [ SQLite Database ]                           [ WebSocket Broadcast ]
         (motor_readings / commands)                        (Live push to Dashboard)
                      │                                             │
                      └──────────────────────┬──────────────────────┘
                                             ▼
                                  [ REACT WEB DASHBOARD ]
                                             │
            ┌────────────────────────────────┴────────────────────────────────┐
            ▼                                                                 ▼
 ┌──────────────────────┐                                          ┌──────────────────────┐
 │  LIVE HARDWARE MODE  │                                          │   SIMULATION MODE    │
 │ Source: Real ESP32   │                                          │ Source: Manual Input │
 └──────────┬───────────┘                                          └──────────┬───────────┘
            │                                                                 │
            └────────────────────────────────┬────────────────────────────────┘
                                             ▼
                       [ REUSABLE CONDITION ANALYSIS ENGINE ]
                       (classify_temperature, classify_rpm,
                        classify_current, classify_vibration)
                                             │
                                             ▼
                                ┌───────────────────────────┐
                                │ • Overall Condition       │
                                │ • Condition Score (0 / 8) │
                                │ • Rule-Based Failure Risk │
                                │ • Diagnostic Explanation  │
                                └───────────────────────────┘
```

---

## 🚀 Quick Start Commands

### 1. Start FastAPI Backend Server
```powershell
cd c:\maccccccc\machfail-model\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Accessible at `http://localhost:8000` (Local) and `http://<YOUR_LAN_IP>:8000` (Network).*

### 2. Start Frontend Web Dashboard
```powershell
cd c:\maccccccc\machfail-model\frontend
npm run dev
```
*Dashboard opens at `http://localhost:5173`.*

### 3. Run Automated Tests
```powershell
cd c:\maccccccc\machfail-model\backend
python -m pytest
```
*Executes all 20 unit, integration, boundary, and mode-isolation test cases.*

---

## 📊 Condition Analysis Thresholds & Classification Rules

The unified condition analysis engine evaluates four parameters using strict priority: **`HIGH` > `MEDIUM` > `NORMAL`**.

### 1. Temperature (°C)
| Range | Classification | Score | Diagnostic Message |
| :--- | :--- | :---: | :--- |
| $30.0 \le \text{Temp} < 35.0$ | **`NORMAL`** | $0$ | Nominal thermal operating state |
| $35.0 \le \text{Temp} < 40.0$ | **`MEDIUM`** | $1$ | Elevated temperature detected |
| $40.0 \le \text{Temp} \le 45.0$ | **`HIGH`** | $2$ | High temperature detected |
| Outside $30 - 45^\circ\text{C}$ | **`OUT_OF_RANGE`** | $0$ or $2$ | Thermal operating bounds warning |

### 2. RPM (Shaft Rotational Speed)
| Range | Classification | Score | Diagnostic Message |
| :--- | :--- | :---: | :--- |
| $\text{RPM} > 1000.0$ | **`NORMAL`** | $0$ | Full operational shaft velocity |
| $500.0 \le \text{RPM} \le 1000.0$ | **`MEDIUM`** | $1$ | Moderate RPM detected (1000 is Medium) |
| $\text{RPM} < 500.0$ | **`HIGH`** | $2$ | Low RPM detected (Severe load drag / stall) |

### 3. Current Draw (Amperes)
| Range | Classification | Score | Diagnostic Message |
| :--- | :--- | :---: | :--- |
| $\text{Current} < 1.0\text{ A}$ | **`NORMAL`** | $0$ | Light electrical load |
| $1.0\text{ A} \le \text{Current} < 1.5\text{ A}$ | **`MEDIUM`** | $1$ | Elevated motor current detected (1.0A is Medium) |
| $\text{Current} \ge 1.5\text{ A}$ | **`HIGH`** | $2$ | High motor current detected (1.5A is High) |

### 4. Vibration (g)
| Range | Classification | Score | Diagnostic Message |
| :--- | :--- | :---: | :--- |
| $\text{Vibration} \le 2000.0\text{ g}$ | **`NORMAL`** | $0$ | Smooth mechanical rotation |
| $2000.0\text{ g} < \text{Vibration} \le 3000.0\text{ g}$ | **`MEDIUM`** | $1$ | Elevated vibration detected |
| $\text{Vibration} > 3000.0\text{ g}$ | **`HIGH`** | $2$ | High vibration detected (Mechanical imbalance) |

### 5. Condition Score & Failure Risk
- **Condition Score**: $\text{Total} = S_{\text{temp}} + S_{\text{rpm}} + S_{\text{current}} + S_{\text{vibration}}$ (Range: $0$ to $8$).
- **Overall Condition**:
  - If **ANY** parameter is `HIGH` $\rightarrow$ **`HIGH`**
  - Else if **ANY** parameter is `MEDIUM` $\rightarrow$ **`MEDIUM`**
  - Else $\rightarrow$ **`NORMAL`**
- **Failure Risk Assessment**:
  - `NORMAL` $\rightarrow$ **`LOW`**
  - `MEDIUM` $\rightarrow$ **`MEDIUM`**
  - `HIGH` $\rightarrow$ **`HIGH`**
  - *Assessment Type: `RULE-BASED FAILURE RISK` (No fabricated ML percentages).*

---

## 🎛️ Live Hardware Mode vs Simulation Mode

| Feature | Live Hardware Mode | Simulation Mode |
| :--- | :--- | :--- |
| **Badge** | `MODE: LIVE HARDWARE \| Source: ESP32` | `MODE: SIMULATION \| Source: Manual Input` |
| **Data Source** | Real sensors via ESP32 Wi-Fi POST | User-entered parameters in dashboard |
| **Motor Control** | Dispatches real commands to ESP32 L298N | **Disabled** (Cannot actuate physical motor) |
| **Database Persistence** | Real timestamped records saved to SQLite | **Isolated** (Zero database writes) |
| **Analysis Engine** | `condition_service.py` | `condition_service.py` (Same unified logic) |

---

## 📡 ESP32 Arduino C++ Firmware Integration

Flash the following sketch onto your ESP32 in the Arduino IDE:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Replace with your PC's IPv4 address on your Wi-Fi network (from ipconfig)
const char* backendHost = "http://192.168.1.100:8000";

// Pins
const int MOTOR_PWM_PIN = 18;
const int MOTOR_IN1_PIN = 19;
const int MOTOR_IN2_PIN = 21;

void setup() {
  Serial.begin(115200);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi: CONNECTED");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    sendTelemetry();
    pollPendingCommands();
  } else {
    Serial.println("WiFi: DISCONNECTED");
  }
  delay(1000); // 1-second transmission interval
}

void sendTelemetry() {
  HTTPClient http;
  String url = String(backendHost) + "/api/motor/data";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Read your real physical sensors here
  float tempVal = 32.9;
  float humVal  = 71.0;
  int irState   = 0;
  long pulses   = 5516;
  float rpmVal  = 1340.7;
  int acsAdc    = 541;
  float currVal = 0.00;
  float mpuX    = 0.01;
  float mpuY    = 0.09;
  float mpuZ    = -0.46;
  float totAcc  = 0.965;
  float vibVal  = 0.035;
  int pwmVal    = 255;

  StaticJsonDocument<512> doc;
  doc["motor_id"]           = "M001";
  doc["status"]             = "ON";
  doc["temperature"]        = tempVal;
  doc["humidity"]           = humVal;
  doc["ir"]                 = irState;
  doc["ir_pulses"]          = pulses;
  doc["rpm"]                = rpmVal;
  doc["acs_adc"]            = acsAdc;
  doc["current"]            = currVal;
  doc["mpu_x"]              = mpuX;
  doc["mpu_y"]              = mpuY;
  doc["mpu_z"]              = mpuZ;
  doc["total_acceleration"] = totAcc;
  doc["vibration"]          = vibVal;
  doc["vibration_level"]    = "LOW";
  doc["motor_pwm"]          = pwmVal;
  doc["voltage"]            = nullptr;
  doc["esp32_ip"]           = WiFi.localIP().toString();

  String payload;
  serializeJson(doc, payload);

  int code = http.POST(payload);
  if (code > 0) {
    Serial.printf("[Backend: CONNECTED] Telemetry sent successfully. HTTP: %d\n", code);
  } else {
    Serial.printf("[Backend: OFFLINE] HTTP POST failed: %s\n", http.errorToString(code).c_str());
  }
  http.end();
}

void pollPendingCommands() {
  HTTPClient http;
  String url = String(backendHost) + "/api/motor/command/M001";
  http.begin(url);

  int code = http.GET();
  if (code == 200) {
    String resp = http.getString();
    StaticJsonDocument<256> doc;
    deserializeJson(doc, resp);

    if (doc["has_pending_command"] == true) {
      String cmd = doc["command"].as<String>();
      String cmdId = doc["command_id"].as<String>();

      if (cmd == "ON") {
        digitalWrite(MOTOR_IN1_PIN, HIGH);
        digitalWrite(MOTOR_IN2_PIN, LOW);
        analogWrite(MOTOR_PWM_PIN, 255);
      } else if (cmd == "OFF") {
        digitalWrite(MOTOR_IN1_PIN, LOW);
        digitalWrite(MOTOR_IN2_PIN, LOW);
        analogWrite(MOTOR_PWM_PIN, 0);
      }

      // Acknowledge execution
      ackCommand(cmdId, "EXECUTED");
    }
  }
  http.end();
}

void ackCommand(String cmdId, String status) {
  HTTPClient http;
  String url = String(backendHost) + "/api/motor/command/ack";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<128> doc;
  doc["motor_id"] = "M001";
  doc["command_id"] = cmdId;
  doc["status"] = status;

  String body;
  serializeJson(doc, body);
  http.POST(body);
  http.end();
}
```

---

## 🛠️ REST API Specification

| Endpoint | Method | Payload / Params | Purpose |
| :--- | :---: | :--- | :--- |
| `/api/motor/data` | `POST` | `MotorSensorDataIn` JSON | Ingests real ESP32 telemetry, stores in SQLite, and pushes to WebSocket |
| `/api/motor/latest` | `GET` | `?motor_id=M001` | Returns latest real telemetry record |
| `/api/motor/status` | `GET` | `?motor_id=M001` | Returns online/offline state and runtime tracking |
| `/api/motor/history/{motor_id}`| `GET` | `?limit=50` | Returns historical records from SQLite |
| `/api/motor/control` | `POST` | `{"motor_id":"M001","command":"ON"}` | Queues motor command |
| `/api/motor/command/{motor_id}`| `GET` | — | Polled by ESP32 for pending commands |
| `/api/motor/command/ack` | `POST` | `{"motor_id":"M001","command_id":"...","status":"EXECUTED"}` | Confirms physical motor actuation |
| `/api/motor/analyze` | `POST` | `{"motor_id":"...","temperature":...,"rpm":...,"current":...,"vibration":...}` | Condition analysis endpoint used by Simulation Mode |
| `/api/motor/condition/{motor_id}` | `GET` | — | Performs condition analysis on the latest real telemetry |
| `/ws/motor/{motor_id}` | `WS` | — | Real-time WebSocket stream pushing telemetry + condition packet |

---

## ✅ Final Integration Verification Checklist

- [x] **ESP32 Telemetry Ingestion**: `POST /api/motor/data` accepts and validates full payload including `ir_pulses`, `rpm`, `motor_pwm`.
- [x] **Database Storage**: SQLite `motor_readings` table stores timestamped physical readings.
- [x] **Live Hardware Dashboard**: Live Monitoring and Overview cards display real readings without hardcoded fake values.
- [x] **Motor Actuation**: `POST /api/motor/control` queues commands, distinguishes requested vs actual state.
- [x] **Unified Condition Analysis**: `condition_service.py` evaluates all 4 physical channels.
- [x] **Rule-Based Failure Risk**: Calculated as LOW / MEDIUM / HIGH with zero artificial percentage claims.
- [x] **Simulation Mode**: Complete with manual inputs, validation error handling, presets, and 100% isolation from physical hardware.
- [x] **Automated Tests**: 20/20 test cases passing.
