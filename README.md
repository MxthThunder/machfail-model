# Industrial Machine Monitoring & Predictive Maintenance (AI Subsystem)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-40%20passed-brightgreen.svg)]()

An explainable, robust, and presentation-ready **Machine Learning & Predictive Maintenance Subsystem** designed to monitor a DC motor setup in real time and predict machine health conditions before failure occurs.

---

## 📌 Team Architecture & Person 3's Role

```
Physical Machine (Motor & Load)
       ↓
Sensors (IR RPM, MPU6050 Vibration, ACS712 Current, DHT22 Temp/Humidity)
       ↓
ESP32 Microcontroller (Person 1 - Hardware)
       ↓ (Wi-Fi / HTTP POST JSON)
AI Prediction API (Person 3 - This Subsystem)
       ├── Machine Condition Classification (0=NORMAL, 1=WARNING, 2=FAULT)
       ├── Explainable Machine Health Score (0 - 100)
       ├── Contributing Diagnostic Factors Breakdown
       └── Uncertainty-Aware Engineering Predictions
       ↓ (HTTP REST)
Web Dashboard (Person 2 - Frontend)
```

- **Person 1 (Hardware):** Microcontroller reading sensors and streaming JSON over Wi-Fi.
- **Person 2 (Web Dashboard):** Visual web interface rendering real-time telemetry, health gauges, and alert banners.
- **Person 3 (AI / Predictive Maintenance - This Repository):** Data pipeline, ML classifiers, health scoring algorithm, diagnostic explanations, and FastAPI microservice.

---

## 🗂️ Project Structure

```
IoT mach/
│
├── data/
│   ├── raw/                           # Raw telemetry datasets
│   │   ├── synthetic_machine_data.csv # 1,200 rows of physics-correlated telemetry
│   │   └── real_machine_data.csv      # Placeholder for Person 1 real sensor recordings
│   ├── processed/                     # Preprocessed train/test splits & plots
│   │   ├── train.csv                  # 80% Stratified training set (960 rows)
│   │   ├── test.csv                   # 20% Stratified testing set (240 rows)
│   │   └── plots/                     # 10 Saved high-resolution diagnostic charts
│   └── sample/                        # Sample JSON payloads (normal, warning, fault)
│
├── docs/
│   ├── setup_guide.md                 # Virtual environment & installation guide
│   ├── dashboard_integration.md       # API specifications & client recipes for Person 2
│   ├── dashboard_preview.html         # Standalone browser UI client for live demos
│   └── presentation_notes.md          # Viva & presentation talking points
│
├── models/
│   ├── model.joblib                   # Serialized RandomForestClassifier
│   ├── scaler.joblib                  # Serialized StandardScaler fitted on train data
│   └── metadata.json                  # Model version, metrics, hyperparameters & provenance
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # EDA and distribution analysis
│   ├── 02_training.ipynb              # Baseline vs candidate ML model benchmarks
│   └── 03_evaluation.ipynb            # Holdout error analysis & confusion matrix
│
├── scripts/
│   ├── generate_sample_data.py        # Configurable physics-correlated synthetic generator
│   ├── run_eda.py                     # Generates all 8 EDA diagnostic plots
│   └── simulate_esp32_stream.py       # Live ESP32 hardware streaming simulator
│
├── src/
│   ├── __init__.py
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
│   ├── test_setup.py                  # Environment & path configuration tests
│   ├── test_data_generation.py        # Synthetic generator tests
│   ├── test_data_loader.py            # Validation & boundary tests
│   ├── test_eda.py                    # Plot rendering tests
│   ├── test_preprocessing.py          # Leakage-free scaling & split tests
│   ├── test_train.py                  # Model training & serialization tests
│   ├── test_evaluate.py               # Evaluation metric thresholds tests
│   ├── test_health_score.py           # Health score formula & band tests
│   ├── test_predictor.py              # Inference & confidence tests
│   ├── test_api.py                    # FastAPI endpoint & Pydantic schema tests
│   ├── test_esp32_integration.py      # Hardware stream latency & transition tests
│   └── test_feature_engineering.py    # Temporal features & causality tests
│
├── requirements.txt                   # Lightweight pinned dependencies
├── .gitignore                         # Git exclusion rules
└── README.md                          # Master documentation
```

---

## 📊 Standard Sensor Schema & Target Classes

| Sensor Feature | Hardware Component | Physical Meaning | Units |
| :--- | :--- | :--- | :--- |
| `rpm` | IR Optical Sensor | Motor rotational speed | RPM |
| `temperature` | DHT22 Sensor | Surface / ambient temperature | °C |
| `humidity` | DHT22 Sensor | Relative ambient humidity | % |
| `current` | ACS712 Sensor | Motor electrical current draw | Amperes (A) |
| `vibration` | MPU6050 Accelerometer | Mechanical vibration intensity | g |

### Target Operating Conditions (`status`)
- `0`: **NORMAL** - Nominal operating speed ($\approx 1500\text{ RPM}$), low vibration ($< 0.15\text{g}$), nominal current ($\approx 0.72\text{A}$).
- `1`: **WARNING** - Speed sag ($1350 - 1420\text{ RPM}$), rising temperature ($38 - 46^\circ\text{C}$), increased current ($0.88 - 1.05\text{A}$).
- `2`: **FAULT** - Severe speed loss ($< 1100\text{ RPM}$), critical thermal build-up ($> 48^\circ\text{C}$), high current ($> 1.30\text{A}$), heavy vibration ($> 0.45\text{g}$).

---

## 🚀 Step-by-Step Reproduction Guide

### 1. Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Dataset & Run Validation
```powershell
python scripts/generate_sample_data.py --samples 1200
python src/data_loader.py
```

### 3. Generate Exploratory Plots & Preprocess Data
```powershell
python scripts/run_eda.py
python src/preprocessing.py
```

### 4. Train Models & Evaluate Holdout Set
```powershell
python src/train.py
python src/evaluate.py
```

### 5. Launch the Real-Time Prediction API
```powershell
uvicorn src.api:app --reload --port 8000
```
- Open Swagger UI: **`http://127.0.0.1:8000/docs`**
- Open Live Dashboard Preview: Double-click [`docs/dashboard_preview.html`](docs/dashboard_preview.html)

### 6. Simulate Live ESP32 Hardware Telemetry
In a separate terminal while the API is running:
```powershell
python scripts/simulate_esp32_stream.py --count 12 --interval 1.0
```

---

## 🧪 Running the Full Automated Test Suite

Execute all 40 unit and integration tests:
```powershell
pytest
```
*Expected: `40 passed in ~18s`.*

---

## 🔄 Retraining Workflow When Real ESP32 Data Arrives

When Person 1 collects real machine logs:
1. Save the labeled physical dataset into `data/raw/real_machine_data.csv`.
2. Ensure the CSV includes `timestamp,rpm,temperature,humidity,current,vibration,status,data_source` (`data_source: real`).
3. Run the preprocessing and training pipeline on the real file:
   ```powershell
   python src/preprocessing.py --input data/raw/real_machine_data.csv
   python src/train.py
   python src/evaluate.py
   ```
4. `models/metadata.json` will automatically update its provenance tag to reflect real machine training.

---

## 📚 Documentation & Presentation Links
- 📘 [Setup Guide](docs/setup_guide.md)
- 📗 [Dashboard Integration Spec (For Person 2)](docs/dashboard_integration.md)
- 📙 [Viva & Presentation Notes](docs/presentation_notes.md)
- 🖥️ [Live Dashboard Preview Client](docs/dashboard_preview.html)
