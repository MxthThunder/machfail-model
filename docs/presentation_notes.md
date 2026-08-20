# 🎓 Student Project Presentation Notes & Defense Guide
## Industrial Machine Monitoring & Predictive Maintenance AI Subsystem (Person 3)

Use these notes to prepare for your project presentation, demo, or viva examination. All concepts are explained in simple, clear, student-friendly engineering language.

---

## 1. The Core Problem: Why Predictive Maintenance?

In industry, there are three maintenance strategies:
1. **Reactive Maintenance (Run-to-Failure):** Fix the machine only after it burns out or breaks.
   - *Downside:* Expensive repairs, catastrophic physical destruction, unexpected factory downtime.
2. **Preventive Maintenance (Calendar-Based):** Replace motor parts every 6 months regardless of condition.
   - *Downside:* Wasteful; replaces healthy components too early, but can still miss sudden unexpected faults.
3. **Predictive Maintenance (Condition-Based AI - Our System):** Continuously monitor physical sensors to detect early signs of mechanical degradation and intervene **before** failure occurs.
   - *Advantage:* Maximizes component lifespan, eliminates surprise downtime, and ensures operator safety.

---

## 2. Sensor Roles: Why Multiple Sensors are Better Than One

| Sensor | Physical Metric | Why It Matters for Motor Health |
| :--- | :--- | :--- |
| **IR Sensor** | **RPM** (Speed) | When bearings wear out or the shaft binds, mechanical drag causes the rotational speed to sag. |
| **DHT22** | **Temperature** (°C) | Mechanical friction and high electrical resistance produce heat ($I^2R$ power loss). Thermal buildup is a classic indicator of stress. |
| **DHT22** | **Humidity** (%) | Acts as an ambient environmental control variable to prevent false alarms due to atmospheric shifts. |
| **ACS712** | **Current** (A) | A DC motor draws more current to maintain torque when fighting friction or heavy mechanical load. |
| **MPU6050** | **Vibration** (g) | Mechanical eccentricity, loose mountings, or defective bearings produce characteristic vibration spikes. |

### 💡 Why Sensor Fusion? (Why not just use a temperature sensor?)
A single sensor can easily fool you:
- High temperature alone could just mean a hot summer day.
- High vibration alone could just mean someone bumped the workbench.
- **Combined Pattern:** If **Current climbs + RPM drops + Vibration rises + Temperature surges**, the AI knows with near-100% certainty that the motor is seizing up!

---

## 3. Machine Learning Model: Why Random Forest?

We evaluated multiple algorithms:
1. **Dummy Baseline:** Achieves $70.9\%$ accuracy simply by guessing "NORMAL" every time, but misses **100% of faults**.
2. **Logistic Regression:** Fast, but assumes purely linear boundaries.
3. **Decision Tree:** Intuitive, but prone to high variance and noisy splits.
4. **Random Forest Classifier (Selected):**
   - Combines an ensemble of 100 decision trees (`n_estimators=100`).
   - Uses `class_weight="balanced"` to pay special attention to rare faults ($7.6\%$).
   - Resistant to overfitting and sensor noise.
   - Executes inferences in $< 5\text{ms}$ on standard CPU (no GPU needed!).
   - Provides transparent **Feature Importance** percentages.

---

## 4. Machine Learning Metrics Explained in Simple Words

| Metric | What It Means | Why It Matters Here |
| :--- | :--- | :--- |
| **Accuracy** | Total correct predictions $\div$ Total predictions. | Misleading on imbalanced data (e.g. Dummy classifier got $70.9\%$ accuracy with $0\%$ fault detection). |
| **Precision** | "When the AI claims it's a FAULT, how often is it actually right?" | High precision means few false alarms. |
| **Recall** | "Out of all actual FAULTS that occurred, how many did the AI catch?" | **The Most Critical Metric.** High recall means zero missed breakdowns. |
| **F1-Score** | Harmonic balance between Precision and Recall. | The best overall measure of model quality across all 3 classes. |

### 🛡️ False Positives vs. False Negatives
- **False Positive (FP):** AI warns of a fault, but the machine is fine. $\to$ *A technician spends 2 minutes checking the motor. No damage done.*
- **False Negative (FN):** The motor is burning out, but AI reports NORMAL. $\to$ *Motor burns out, fire hazard, complete system failure.*
- **Takeaway:** In industrial AI, **maximizing FAULT Recall is paramount**.

---

## 5. How the Machine Health Score ($0 - 100$) Works

Our health score is completely explainable (not a black box):
1. **Base Score ($0 - 100$):** Weighted combination of model probabilities:
   $$\text{Base} = (1.00 \times P_{\text{NORMAL}} + 0.80 \times P_{\text{WARNING}} + 0.00 \times P_{\text{FAULT}}) \times 100$$
2. **Sensor Strain Deduction ($0 - 10\text{ pts}$):** Small deductions if individual sensors cross physical thresholds (e.g. Temp $> 38^\circ\text{C}$, Current $> 0.85\text{A}$, Vib $> 0.20\text{g}$).
3. **Classification Bands:**
   - **$90 - 100$:** **NORMAL** (Healthy)
   - **$70 - 89$:** **WARNING** (Moderate stress, inspection recommended)
   - **$0 - 69$:** **HIGH RISK / FAULT** (Imminent failure)

---

## 6. Real Data vs. Synthetic Data (Safety & Scientific Honesty)

If an evaluator asks: *"Did you train this on real motor failures?"*
**Your Honest Answer:**
> *"The development model was trained on a physics-correlated synthetic dataset to establish the pipeline and API contracts. The dataset explicitly tags all rows as `data_source: synthetic`. Once Person 1 completes physical motor runs, the model will be retrained using `data/raw/real_machine_data.csv` using the exact same pipeline."*

---

## 7. What the AI Cannot Guarantee (Limitations)
- **Predictive Correlation vs. Causation:** The model identifies sensor patterns associated with conditions; it cannot guarantee the exact microscopic metallurgical cause (e.g., inner-race vs outer-race bearing crack).
- **Physical Sensor Drift:** If an analog sensor gets miscalibrated, the AI's predictions will drift until recalibrated.
