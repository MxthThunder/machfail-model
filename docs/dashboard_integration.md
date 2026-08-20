# Web Dashboard Integration Guide (For Person 2)

Welcome, Person 2! This document provides the complete API specification, data contracts, and client integration code for connecting your **Web Dashboard** to the **Person 3 AI Prediction Microservice**.

---

## 1. 🌐 API Service Overview

- **Base URL (Localhost):** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **CORS Status:** **Enabled** (`*`) — you can call this API directly from `localhost:3000`, `localhost:5173` (Vite), or any local development server without CORS errors.

---

## 2. 📡 Endpoints Specification

### 2.1 `POST /predict` (Core Inference)
Sends real-time or aggregated sensor telemetry to the AI engine and receives condition classification, continuous health scores, and contributing diagnostic explanations.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Payload (`JSON`)
| Field | Type | Description | Valid Range | Example |
| :--- | :--- | :--- | :--- | :--- |
| `rpm` | `float` | Motor rotational speed in RPM | `0.0` to `3000.0` | `1380.0` |
| `temperature` | `float` | Motor surface/ambient temp in °C | `-10.0` to `120.0` | `42.5` |
| `humidity` | `float` | Relative ambient humidity in % | `0.0` to `100.0` | `62.0` |
| `current` | `float` | Motor current draw in Amperes | `0.0` to `10.0` | `0.98` |
| `vibration` | `float` | Vibration intensity in g | `0.0` to `5.0` | `0.28` |

#### Example Request Body
```json
{
    "rpm": 1380.0,
    "temperature": 42.5,
    "humidity": 62.0,
    "current": 0.98,
    "vibration": 0.28
}
```

#### Example Response (`200 OK`)
```json
{
    "status": "WARNING",
    "status_code": 1,
    "health_score": 75,
    "health_category": "WARNING",
    "confidence": 0.88,
    "prediction": "Sensor pattern is consistent with possible motor overload, elevated thermal stress, or developing friction.",
    "probabilities": {
        "NORMAL": 0.10,
        "WARNING": 0.88,
        "FAULT": 0.02
    },
    "contributing_factors": [
        "Elevated temperature (42.5 C) exceeds nominal baseline (32.0 C).",
        "Increased current draw (0.98 A) above nominal (0.72 A).",
        "Elevated vibration (0.280 g) higher than nominal smooth baseline (0.1 g)."
    ],
    "timestamp": "2026-08-20T10:14:40.123456",
    "model_version": "1.0.0"
}
```

---

### 2.2 `GET /health` (Service Liveness)
Checks if the AI engine is running and ready to receive requests.

#### Response (`200 OK`)
```json
{
    "status": "ok",
    "service": "industrial-ai-prediction-service",
    "version": "1.0.0"
}
```

---

### 2.3 `GET /model-info` (Model Provenance & Metadata)
Fetches model name, version, training date, hyperparameters, and active features for display on an "About" or "System Status" dashboard tab.

---

## 3. 🎨 UI & Design Recommendations for Person 2

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MACHINE HEALTH DASHBOARD                                 │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────┤
│ Machine Health Score         │ Machine Operating Status     │ Prediction Confidence    │
│            75%               │        ⚠️ WARNING           │          88.0%           │
│ (Circular Gauge: 0 - 100)    │ (Color Badge)                │ (Confidence Bar)         │
├──────────────────────────────┴──────────────────────────────┴──────────────────────────┤
│ Diagnostic Summary:                                                                    │
│ "Sensor pattern is consistent with possible motor overload or developing friction."    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Contributing Diagnostic Factors:                                                       │
│ • Elevated temperature (42.5°C) exceeds nominal baseline (32.0°C).                     │
│ • Increased current draw (0.98 A) above nominal (0.72 A).                              │
│ • Elevated vibration (0.280 g) higher than nominal smooth baseline (0.1 g).            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Recommended UI Color Palette
- **NORMAL ($90 - 100$):** Green (`#22c55e` / `rgb(34, 197, 94)`)
- **WARNING ($70 - 89$):** Amber / Orange (`#f59e0b` / `rgb(245, 158, 11)`)
- **FAULT ($0 - 69$):** Red (`#ef4444` / `rgb(239, 68, 68)`)

---

## 4. 💻 Client Code Examples

### 4.1 Vanilla JavaScript (Fetch API)
```javascript
async function fetchPrediction(sensorData) {
    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(sensorData),
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        console.log("Prediction Received:", data);
        
        // Update your UI elements
        document.getElementById("health-score").innerText = `${data.health_score}%`;
        document.getElementById("status-badge").innerText = data.status;
        document.getElementById("prediction-text").innerText = data.prediction;
        
        return data;
    } catch (error) {
        console.error("Failed to fetch prediction:", error);
    }
}
```

### 4.2 React Hook Example (`useMachinePrediction.js`)
```jsx
import { useState, useEffect } from "react";

export function useMachinePrediction(sensorTelemetry, pollIntervalMs = 2000) {
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!sensorTelemetry) return;

        const getPrediction = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(sensorTelemetry),
                });
                if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
                const data = await res.json();
                setPrediction(data);
                setError(null);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        getPrediction();
        const interval = setInterval(getPrediction, pollIntervalMs);
        return () => clearInterval(interval);
    }, [sensorTelemetry, pollIntervalMs]);

    return { prediction, loading, error };
}
```

---

## 5. 🔍 Interactive Test Page

You can open [`docs/dashboard_preview.html`](dashboard_preview.html) directly in any web browser to test sending live simulated sensor sliders to the AI API!
