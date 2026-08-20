Design a modern, professional web dashboard for an Industrial Machine Monitoring and Predictive Maintenance System.

PROJECT PURPOSE:
This dashboard is used by an industrial engineer to remotely monitor and control multiple machines/motors in a factory. Only one physical motor (MOTOR-01) is currently connected to the system. The other motors are realistic placeholder machines demonstrating how the system can scale to an industrial environment.

IMPORTANT:
There is NO LOGIN PAGE.
The website opens directly to the machine overview/dashboard.

DESIGN STYLE:
- Professional industrial IoT / Industry 4.0 interface
- Modern, clean, technical, premium appearance
- Dark industrial theme
- Use dark charcoal/navy backgrounds
- Use blue as the primary accent
- Green for healthy/online
- Yellow/orange for warnings
- Red for critical faults
- High contrast and excellent readability
- Rounded cards, subtle borders, subtle shadows
- Avoid excessive gradients and excessive decorative elements
- The interface should look like a real industrial monitoring product, not a generic admin dashboard
- Responsive desktop-first design
- Use consistent spacing, typography, icons and component styles

MAIN LAYOUT:
Create a fixed left sidebar and a top header.

LEFT SIDEBAR:
Logo:
"INDUSTRIA"
Subtitle:
"Machine Intelligence"

Navigation:
- Overview
- Machines
- Live Monitoring
- Motor Control
- Analytics
- Alerts
- AI Prediction

At the bottom:
- System Status
- "ESP32 Network: Connected"

TOP HEADER:
- Page title
- Selected machine name when applicable
- Connection status
- Last data update time
- Notification icon
- User label: "Engineer"

PAGE 1 — OVERVIEW / MACHINE FLEET:

Create a machine overview page.

Top summary cards:
- Total Machines: 6
- Online: 1
- Offline: 5
- Active Alerts: 0

Create a grid of 6 machine cards.

MOTOR-01:
- Realistic industrial electric motor image
- Name: MOTOR-01
- Type: Conveyor Motor
- Status: ONLINE
- Green status indicator
- Health: 92%
- RPM: 1450
- Button: "View Machine"

MOTOR-02:
- Industrial pump/motor image
- Name: MOTOR-02
- Type: Pump Motor
- Status: OFFLINE
- Health: -- 
- Button: "View Machine"

MOTOR-03:
- Industrial motor image
- Type: Compressor Motor
- OFFLINE

MOTOR-04:
- Industrial motor image
- Type: Cooling Motor
- OFFLINE

MOTOR-05:
- Industrial motor image
- Type: Conveyor Motor
- OFFLINE

MOTOR-06:
- Industrial motor image
- Type: Hydraulic Motor
- OFFLINE

Make the cards visually attractive and clearly distinguish ONLINE and OFFLINE states.

When MOTOR-01 is selected, navigate to the detailed machine page.

PAGE 2 — MOTOR-01 MACHINE DETAILS:

Header:
"← Back to Machines"
"MOTOR-01"
"Conveyor Motor"

Show:
ONLINE status only when the machine is actually running and communicating with the ESP32.

Create a machine overview section.

LIVE SENSOR CARDS:
- RPM: 1450 RPM
- Temperature: 42.5 °C
- Humidity: 58%
- Current: 1.2 A
- Voltage: 9.1 V
- Vibration: NORMAL

Each card should have:
- Sensor icon
- Current value
- Unit
- Status indicator
- Small trend indicator

Add a large LIVE STATUS graph.

Allow the engineer to select:
- RPM
- Temperature
- Current
- Voltage
- Vibration

Time filters:
- 1 minute
- 5 minutes
- 1 hour
- 24 hours

PAGE 3 — MOTOR CONTROL:

Create a professional motor-control panel.

Show:
Motor status: RUNNING / STOPPED
Current RPM
Current temperature
Current draw

Controls:
- START button
- STOP button
- EMERGENCY STOP button
- Speed slider from 0–100%

Display:
"Commanded Speed: 65%"
"Actual RPM: 1450"

Make the emergency stop visually prominent but not excessive.

Show a small explanation:
"Commands are sent to the ESP32 through the connected network."

PAGE 4 — ANALYTICS:

Create historical analytics.

Include:
- RPM history graph
- Temperature history graph
- Current history graph
- Voltage history graph
- Vibration history graph

Allow date/time filtering:
- Last hour
- Today
- 7 days
- 30 days

Include summary statistics:
- Average RPM
- Maximum temperature
- Average current
- Maximum vibration
- Total runtime

PAGE 5 — ALERTS:

Create an industrial alert-management page.

Top summary:
- Critical
- Warning
- Informational

Alert examples:

CRITICAL:
"Abnormal motor current detected"
Current: 2.8 A

WARNING:
"Temperature approaching threshold"
Temperature: 58 °C

INFO:
"Motor started"
Time: 10:30 AM

Each alert should include:
- Severity
- Machine
- Description
- Sensor value
- Timestamp
- Status

Use:
Green = normal
Yellow = warning
Red = critical

PAGE 6 — AI PREDICTION:

IMPORTANT:
AI prediction must NOT automatically run when the page opens.

Create a prominent button:

"🔮 PREDICT MACHINE HEALTH"

Before prediction:
Display:
"Prediction has not been run yet."
"Click Predict Machine Health to analyze the latest machine sensor data."

After the engineer clicks the button, show a loading state:
"Analyzing machine data..."
"Running predictive maintenance model..."

Then display:

MACHINE HEALTH:
87%

FAILURE PROBABILITY:
8%

PREDICTION:
NORMAL

RISK:
LOW

RECOMMENDATION:
"Continue normal operation."

Include a "Predict Again" button.

Also design warning and critical prediction states.

WARNING example:
Health: 58%
Failure probability: 42%
Prediction: Possible abnormal motor behavior
Recommendation: Inspect machine condition.

CRITICAL example:
Health: 32%
Failure probability: 78%
Prediction: Possible motor/bearing fault
Recommendation: Inspect machine immediately.

IMPORTANT AI DATA:
The model will eventually receive:
- RPM
- Temperature
- Humidity
- Current
- Voltage
- Vibration

PAGE 7 — SYSTEM STATUS:

Create a small system-health panel showing:

ESP32:
Connected

Wi-Fi:
Connected

RPM Sensor:
Connected

DHT22:
Connected

MPU6050:
Connected

ACS712:
Connected

Motor:
Running

Show connection indicators.

ONLINE/OFFLINE LOGIC:
Do NOT make the machine ONLINE merely because the dashboard is open.

MOTOR-01 should show ONLINE only when:
1. The motor is running/active, AND
2. The ESP32 is communicating with the backend.

When the motor is OFF:
Show:
"OFFLINE"
and do not display fake live sensor values.

You may display the last recorded values separately with a label:
"Last recorded".

OTHER MOTORS:
MOTOR-02 through MOTOR-06 are placeholders only.
They should be visually realistic but clearly show OFFLINE.

DESIGN SYSTEM:
Create reusable components for:
- Sidebar
- Header
- Machine cards
- Sensor cards
- Status badges
- Buttons
- Alert cards
- Graph containers
- AI prediction cards
- Machine status indicators
- Modal/dialog
- Loading state
- Empty state
- Offline state

Use a consistent 8px spacing system.

Typography should be clean and technical, preferably Inter or a similar modern sans-serif.

Create desktop design at approximately 1440 × 1024.

Also create responsive versions for tablet and mobile.

INTERACTION / PROTOTYPE:
Prototype these flows:

1. Overview → click MOTOR-01 → Motor Details
2. Motor Details → Live Monitoring
3. Motor Details → Motor Control
4. Motor Details → Analytics
5. Motor Details → AI Prediction
6. AI Prediction → click "Predict Machine Health" → Loading → Prediction Result
7. Sidebar navigation between all major sections
8. Start/Stop controls should have appropriate confirmation feedback
9. Emergency Stop should show a confirmation/alert state
10. Offline machines should show an appropriate offline state when opened

Make the final Figma design polished enough to look like a real industrial IoT SaaS product and suitable for a college engineering project demonstration.