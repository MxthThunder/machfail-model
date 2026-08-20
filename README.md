# Industrial Machine Monitoring & Predictive Maintenance (AI Subsystem & INDUSTRIA Dashboard)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19+-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8+-646CFF.svg)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-40%20passed-brightgreen.svg)]()

An explainable, robust, and presentation-ready **Machine Learning & Predictive Maintenance Subsystem** and accompanying **INDUSTRIA React Dashboard** designed to monitor an industrial DC motor setup in real time and predict machine health conditions before failure occurs.

---

## 📌 Complete System Architecture

```
Physical Machine (Motor & Load)
       ↓
Sensors (IR RPM, MPU6050 Vibration, ACS712 Current, DHT22 Temp/Humidity)
       ↓
ESP32 Microcontroller (Person 1 - Hardware)
       ↓ (Wi-Fi / HTTP POST JSON)
AI Prediction API (Person 3 - Python FastAPI Backend)
       ├── Machine Condition Classification (0=NORMAL, 1=WARNING, 2=FAULT)
       ├── Explainable Machine Health Score (0 - 100)
       ├── Contributing Diagnostic Factors Breakdown
       └── Uncertainty-Aware Engineering Predictions
       ↓ (HTTP REST JSON)
INDUSTRIA Web Dashboard (React + Vite Frontend)
       ├── Machine Fleet Overview & Status
       ├── Live Sensor Telemetry Charts
       ├── Motor Control Panel (Commands & Speed Slider)
       └── Multi-Step AI Predictive Maintenance Workflow
```

---

## 🗂️ Project Structure

```
machfail-model/
│
├── data/                              # Datasets & diagnostic plots
│   ├── raw/
│   │   ├── synthetic_machine_data.csv # 1,200 rows of physics-correlated telemetry
│   │   └── real_machine_data.csv      # Placeholder for Person 1 real sensor recordings
│   ├── processed/
│   │   ├── train.csv                  # 80% Stratified training set (960 rows)
│   │   ├── test.csv                   # 20% Stratified testing set (240 rows)
│   │   └── plots/                     # 10 High-resolution diagnostic charts
│   └── sample/                        # Sample JSON payloads (normal, warning, fault)
│
├── docs/                              # Guides & documentation
│   ├── setup_guide.md                 # Python & node environment setup
│   ├── dashboard_integration.md       # API specifications & client contracts
│   ├── dashboard_preview.html         # Standalone HTML demo client
│   └── presentation_notes.md          # Viva & presentation talking points
│
├── frontend/                          # INDUSTRIA React + Vite Web Dashboard
│   ├── src/
│   │   ├── pages/                     # Overview, MotorControl, AIPrediction, etc.
│   │   ├── services/api.ts            # Microservice client connecting to FastAPI
│   │   ├── App.tsx                    # Main navigation & dark industrial theme
│   │   ├── main.tsx                   # React root mount
│   │   └── index.css                  # Industrial design system & animations
│   ├── package.json                   # React, Vite, TailwindCSS, Recharts
│   └── vite.config.ts                 # Vite development & build configuration
│
├── models/                            # Serialized ML artifacts
│   ├── model.joblib                   # Serialized RandomForestClassifier
│   ├── scaler.joblib                  # Serialized StandardScaler fitted on train data
│   └── metadata.json                  # Model version, metrics, hyperparameters & provenance
│
├── notebooks/                         # Interactive Jupyter notebooks
│   ├── 01_data_exploration.ipynb      # EDA and distribution analysis
│   ├── 02_training.ipynb              # Baseline vs candidate ML model benchmarks
│   └── 03_evaluation.ipynb            # Holdout error analysis & confusion matrix
│
├── scripts/                           # Automation scripts
│   ├── generate_sample_data.py        # Configurable physics-correlated synthetic generator
│   ├── run_eda.py                     # Generates all 8 EDA diagnostic plots
│   └── simulate_esp32_stream.py       # Live ESP32 hardware streaming simulator
│
├── src/                               # Core Python AI Subsystem
│   ├── config.py                      # Central paths, sensor bounds, classes & random seeds
│   ├── data_loader.py                 # Safe loading & deep integrity validation
│   ├── preprocessing.py               # Feature isolation, stratified split & scaling
│   ├── feature_engineering.py         # Temporal rate-of-change & rolling average features
│   ├── train.py                       # 5-Fold CV benchmark & Random Forest trainer
│   ├── evaluate.py                    # Holdout evaluation & diagnostic plot generator
│   ├── health_score.py                # Explainable 0-100 Machine Health Score algorithm
│   ├── predictor.py                   # High-level inference & explanation engine
│   └── api.py                         # FastAPI microservice (/predict, /health, /model-info)
│
├── tests/                             # 40 Automated unit & integration tests
├── requirements.txt                   # Pinned Python dependencies
└── README.md                          # Master documentation
```

---

## 🚀 How to Run the Complete System

### 1. Start the AI Microservice Backend
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.api:app --reload --port 8000
```
- API Docs: **`http://127.0.0.1:8000/docs`**

### 2. Start the INDUSTRIA Frontend Dashboard
In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```
- Dashboard URL: **`http://localhost:8443/`** (or `http://localhost:5173/`)

---

## 🧪 Testing

```powershell
pytest
```
*40 passed in ~18s.*

---

## 📚 Documentation & Presentation Links
- 📘 [Setup Guide](docs/setup_guide.md)
- 📗 [Dashboard Integration Contract](docs/dashboard_integration.md)
- 📙 [Viva & Presentation Notes](docs/presentation_notes.md)
