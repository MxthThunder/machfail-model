# Python Environment & Setup Guide

This guide helps you set up your local development environment for the **Industrial Machine AI Subsystem (Person 3)**.

---

## 1. Prerequisites
- **Operating System:** Windows 10/11
- **Python Version:** Python 3.10+ (Detected: Python 3.13.x)
- **Terminal:** PowerShell, Command Prompt, or VS Code / Antigravity Integrated Terminal

---

## 2. Step-by-Step Setup

### Step 2.1: Open Terminal in Project Root
Make sure your terminal is in the project directory:
```powershell
cd "c:\IoT mach"
```

### Step 2.2: Create a Virtual Environment (Recommended)
A virtual environment keeps your project packages isolated from global Python packages:
```powershell
python -m venv venv
```

### Step 2.3: Activate the Virtual Environment
On Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell gives a script execution policy warning, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, or activate via Command Prompt: `.\venv\Scripts\activate.bat`)*

When activated, you will see `(venv)` in your terminal prompt.

### Step 2.4: Install Required Packages
Install all required libraries using the pinned `requirements.txt`:
```powershell
pip install -r requirements.txt
```

---

## 3. Verify Your Installation

Run the Stage 1 verification test:
```powershell
python tests/test_setup.py
```
Or using pytest:
```powershell
pytest tests/test_setup.py
```

Expected Output:
```
All Stage 1 setup tests passed successfully!
```

---

## 4. Installed Packages Overview

| Package | Purpose in Project |
| :--- | :--- |
| `pandas` & `numpy` | Data loading, manipulation, and numerical operations |
| `scikit-learn` | Preprocessing, baseline models, Random Forest classifier, metrics |
| `joblib` | Saving and loading trained model artifacts |
| `matplotlib` | Data exploration charts and confusion matrix plots |
| `fastapi` & `uvicorn` | Lightweight REST API for real-time machine predictions |
| `pydantic` | Strict input validation for incoming sensor readings |
| `pytest` | Unit testing pipelines, predictors, and API endpoints |
