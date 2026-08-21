import React, { useState, useEffect } from 'react';

interface SlideData {
  id: number;
  title: string;
  category: string;
  badge: string;
  notes: string;
  render: () => React.ReactNode;
}

export default function Presentation() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showNotes, setShowNotes] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const SLIDES: SlideData[] = [
    {
      id: 1,
      title: "IoT-Based Motor Monitoring & Predictive Maintenance",
      category: "TITLE & TEAM",
      badge: "Industry 4.0 IoT Platform",
      notes: "Welcome to our presentation on the IoT-Based Motor Monitoring and Predictive Maintenance System. Our team combines embedded hardware, cloud/backend software, and machine learning.",
      render: () => (
        <div className="flex flex-col justify-center h-full gap-6">
          <div className="inline-block px-3 py-1 text-xs font-semibold tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-500/40 rounded-full w-fit">
            INDUSTRY 4.0 IoT PLATFORM
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-white">
            IoT-Based Motor Monitoring and<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400">
              Predictive Maintenance System
            </span>
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
            Real-time multi-sensor telemetry collection via ESP32, high-throughput cloud streaming, interactive monitoring dashboard, and predictive machine-learning fault classification.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
            <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80">
              <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">👥 Project Presenters</div>
              <ul className="text-xs text-slate-300 space-y-1.5">
                <li><b className="text-white">Person 1:</b> Hardware Architecture & ESP32 Embedded Systems</li>
                <li><b className="text-white">Person 2:</b> Web Dashboard & FastAPI Backend Architecture</li>
                <li><b className="text-white">Person 3:</b> Machine Learning & Predictive Analytics</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80">
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">⚡ Technology Stack</div>
              <ul className="text-xs text-slate-300 space-y-1.5">
                <li><b className="text-white">Hardware:</b> ESP32 | DHT22 | ACS712 | MPU6050 | IR Sensor</li>
                <li><b className="text-white">Backend:</b> Python | FastAPI | WebSocket | SQLite</li>
                <li><b className="text-white">Frontend & AI:</b> React 19 | TailwindCSS | Scikit-Learn</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 2,
      title: "Introduction — Industrial Motors & Maintenance",
      category: "SYSTEM BACKGROUND",
      badge: "Context & Need",
      notes: "Industrial motors power factories and pumps. Unplanned downtime is extremely expensive. We propose an end-to-end IoT and ML platform.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-3">
            <div className="text-sm font-bold text-amber-400">⚠️ Industrial Context & Downtime Costs</div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Industrial motors are essential in manufacturing plants, pumps, conveyors, compressors, and cooling fans. Unexpected motor failures cause severe production downtime, equipment damage, high repair bills, and safety risks.
            </p>
            <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-lg text-xs text-red-200 space-y-1">
              <div>✖ Unplanned production downtime</div>
              <div>✖ High emergency secondary repair costs</div>
              <div>✖ Equipment insulation breakdown & thermal hazard</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-3">
            <div className="text-sm font-bold text-emerald-400">💡 Our IoT-Based Solution</div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Our project develops an IoT telemetry platform continuously collecting motor temperature, current, vibration, and rotation through sensors connected to an ESP32.
            </p>
            <div className="p-3 bg-cyan-950/40 border border-cyan-800/50 rounded-lg text-xs text-cyan-200 italic leading-relaxed">
              “Our project continuously monitors the condition of an industrial motor using sensors. The ESP32 collects the sensor data and sends it through Wi-Fi to our backend. The dashboard displays live metrics, and ML predicts possible failures.”
            </div>
          </div>
        </div>
      )
    },
    {
      id: 3,
      title: "Project Abstract",
      category: "EXECUTIVE SUMMARY",
      badge: "Platform Overview",
      notes: "This abstract outlines the complete pipeline: hardware edge sensing, cloud backend ingestion, and predictive ML intelligence.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">01. Edge Sensing</div>
            <ul className="text-xs text-slate-300 space-y-1.5">
              <li>• <b>ESP32:</b> 240MHz Dual-Core CPU with 2.4GHz Wi-Fi</li>
              <li>• <b>DHT22:</b> Housing Temp & Humidity</li>
              <li>• <b>ACS712:</b> Hall-Effect Load Current</li>
              <li>• <b>MPU6050:</b> 3-Axis Acceleration & Vibration</li>
              <li>• <b>IR Sensor:</b> Object presence / RPM</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-xs font-bold text-sky-400 uppercase tracking-wider mb-2">02. Cloud Backend</div>
            <ul className="text-xs text-slate-300 space-y-1.5">
              <li>• <b>FastAPI:</b> Asynchronous REST API & WebSockets</li>
              <li>• <b>SQLite:</b> Time-series historical telemetry logging</li>
              <li>• <b>Web Dashboard:</b> Real-time live status gauges</li>
              <li>• <b>Remote Control:</b> Motor speed PWM modulation</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">03. Predictive AI</div>
            <ul className="text-xs text-slate-300 space-y-1.5">
              <li>• <b>Vibration Classification:</b> Low, Med, High grading</li>
              <li>• <b>Anomaly Detection:</b> Thermal drift & current spike alerts</li>
              <li>• <b>Goal:</b> Condition-Based Maintenance</li>
              <li>• <b>Outcome:</b> Minimized downtime & optimized asset life</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 4,
      title: "Target Sector & Application Areas",
      category: "MARKET & SECTOR",
      badge: "Industry 4.0 Scope",
      notes: "Target sector is industrial manufacturing, especially continuous-duty operations where unexpected motor stoppage incurs massive costs.",
      render: () => (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 h-full">
          {[
            { title: "Manufacturing Industries", desc: "Production lines, conveyors, robotic machinery", col: "text-cyan-400" },
            { title: "Pumping Systems", desc: "Water treatment, industrial pumps, cooling loops", col: "text-blue-400" },
            { title: "Industrial HVAC", desc: "Air handling fans, blowers, chiller compressors", col: "text-emerald-400" },
            { title: "Mining & Heavy Industry", desc: "Crushers, ore conveyors, ventilation shafts", col: "text-amber-400" },
            { title: "Process Industries", desc: "Chemical agitators, food mixers, textile spinning", col: "text-purple-400" },
            { title: "Smart Factories", desc: "Integrated Industry 4.0 SCADA & predictive maintenance", col: "text-rose-400" },
          ].map((item, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col justify-center">
              <div className={`text-xs font-bold ${item.col} mb-1`}>{idx + 1}. {item.title}</div>
              <div className="text-[11px] text-slate-300 leading-snug">{item.desc}</div>
            </div>
          ))}
        </div>
      )
    },
    {
      id: 5,
      title: "Problem Statement — Traditional vs Modern",
      category: "PROBLEM ANALYSIS",
      badge: "Comparative Study",
      notes: "Traditional maintenance is periodic and blind to sudden faults. Our IoT solution provides 24/7 continuous health tracking.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">❌ Traditional Maintenance Deficiencies</div>
            <ul className="text-xs text-slate-300 space-y-2 mt-1">
              <li>✖ <b>Periodic Inspections:</b> Blind to rapid faults emerging between maintenance visits.</li>
              <li>✖ <b>Undetected Thermal Drift:</b> Gradual winding overheating goes unnoticed until burnout.</li>
              <li>✖ <b>Vibration Unnoticed:</b> Subtle bearing flaking and shaft misalignment worsen silently.</li>
              <li>✖ <b>High Labor Time:</b> Manual floor walks with handheld tools are labor-intensive.</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">✔️ Proposed IoT Condition Platform</div>
            <ul className="text-xs text-slate-300 space-y-2 mt-1">
              <li>✔ <b>Continuous 24/7 Monitoring:</b> High-frequency sampling of physical variables.</li>
              <li>✔ <b>Instant Edge Alarms:</b> Automated trip warnings on abnormal vibration or current.</li>
              <li>✔ <b>Calibrated Accuracy:</b> 1.8925 V zero-current offset calibration ensures precision.</li>
              <li>✔ <b>Predictive AI Forecasting:</b> Anticipates Remaining Useful Life before breakdown.</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 6,
      title: "System Hardware & Bill of Materials",
      category: "HARDWARE SPECS",
      badge: "Component Pinout",
      notes: "Comprehensive BOM covering the ESP32, sensor array, L298N driver, power supply, and protection circuitry.",
      render: () => (
        <div className="overflow-x-auto h-full">
          <table className="w-full text-left text-xs border border-slate-700/80 rounded-xl overflow-hidden">
            <thead className="bg-slate-800 text-cyan-400 font-bold border-b border-slate-700">
              <tr>
                <th className="p-2.5">Component</th>
                <th className="p-2.5">Interface / Pin</th>
                <th className="p-2.5">Functional Role in System</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              <tr><td className="p-2 font-mono font-semibold text-white">ESP32 Dev Board</td><td className="p-2">Dual Core, Wi-Fi</td><td>Central edge controller, sensor sampling & Wi-Fi transmission</td></tr>
              <tr><td className="p-2 font-mono font-semibold text-white">DHT22 Sensor</td><td className="p-2">GPIO 4 (1-Wire)</td><td>Motor housing temperature & ambient relative humidity</td></tr>
              <tr><td className="p-2 font-mono font-semibold text-white">ACS712 Current</td><td className="p-2">GPIO 34 (ADC1)</td><td>Hall-effect load current transducer (1.8925V calibrated offset)</td></tr>
              <tr><td className="p-2 font-mono font-semibold text-white">MPU6050 IMU</td><td className="p-2">GPIO 21/22 (I2C)</td><td>3-Axis accelerometer for dynamic vibration magnitude vector</td></tr>
              <tr><td className="p-2 font-mono font-semibold text-white">IR Sensor</td><td className="p-2">GPIO 35 (Digital)</td><td>Optical presence / shaft RPM pulse counter</td></tr>
              <tr><td className="p-2 font-mono font-semibold text-white">L298N Driver</td><td className="p-2">GPIO 25, 26, 27</td><td>Dual H-Bridge power driver for motor speed PWM and safety stop</td></tr>
            </tbody>
          </table>
        </div>
      )
    },
    {
      id: 7,
      title: "End-to-End System Architecture",
      category: "SYSTEM DESIGN",
      badge: "Telemetry Pipeline",
      notes: "Architecture moves seamlessly from physical motor sensors to ESP32 edge processing, FastAPI cloud backend, React dashboard, and ML prediction.",
      render: () => (
        <div className="flex flex-col justify-center h-full p-4 rounded-xl bg-slate-900 border border-slate-700/80 font-mono text-[11px] text-cyan-300 overflow-x-auto leading-relaxed">
          <pre>{`┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  PHYSICAL DC MOTOR   │ ───►  │  SENSOR ARRAY NODE   │ ───►  │   ESP32 EDGE NODE    │
│  Industrial Actuator │       │ DHT22/ACS712/MPU6050 │       │ Conversion & Filter  │
└──────────────────────┘       └──────────────────────┘       └──────────┬───────────┘
                                                                         │ Wi-Fi / HTTP
                                                                         ▼
┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ ML PREDICTIVE AI     │ ◄───  │ TIME-SERIES DATABASE │ ◄───  │   FASTAPI BACKEND    │
│ Fault Forecasting    │       │ SQLite / WebSocket   │       │ REST Ingestion & Val │
└──────────┬───────────┘       └──────────────────────┘       └──────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                  REACT WEB OPERATOR DASHBOARD & ALERTS                             │
└────────────────────────────────────────────────────────────────────────────────────┘`}</pre>
        </div>
      )
    },
    {
      id: 8,
      title: "Vibration & Current Mathematical Models",
      category: "EDGE ALGORITHMS",
      badge: "Sensor Mathematics",
      notes: "MPU6050 measures 3D acceleration. We calculate vector magnitude minus 1g gravity to isolate vibration amplitude into Low, Med, and High severity.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">MPU6050 Vibration Vector Math</div>
            <div className="p-3 bg-slate-900 rounded font-mono text-xs text-sky-300">
              Total Accel = √( X² + Y² + Z² )<br/>
              Vibration = | Total Accel - 1.0g |
            </div>
            <div className="text-xs text-slate-300 space-y-1">
              <div>• <b>LOW (&lt; 0.05g):</b> Smooth operation, balanced rotor.</div>
              <div>• <b>MEDIUM (0.05 - 0.15g):</b> Minor imbalance or slight looseness.</div>
              <div>• <b>HIGH (≥ 0.15g):</b> Severe bearing damage or misalignment.</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">ACS712 Current Calibration</div>
            <div className="p-3 bg-slate-900 rounded font-mono text-xs text-emerald-300">
              V_zero_offset = 1.8925 V (Calibrated)<br/>
              Current (A) = (V_sensor - 1.8925) / 0.100
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              100-sample moving average filter removes inductive motor brush commutation spikes and ADC noise.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 9,
      title: "Live Telemetry & Dashboard View",
      category: "OPERATOR UI",
      badge: "Real-Time Monitoring",
      notes: "The dashboard provides plant operators with real-time health indicators, live waveforms, and motor control switches.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col justify-center">
            <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3">Live Motor Telemetry</div>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="p-2 rounded bg-slate-900 text-center">
                <div className="text-[10px] text-slate-400 uppercase">Temp</div>
                <div className="text-base font-bold text-cyan-400">34.4 °C</div>
              </div>
              <div className="p-2 rounded bg-slate-900 text-center">
                <div className="text-[10px] text-slate-400 uppercase">Current</div>
                <div className="text-base font-bold text-sky-400">2.40 A</div>
              </div>
              <div className="p-2 rounded bg-slate-900 text-center">
                <div className="text-[10px] text-slate-400 uppercase">Vibe</div>
                <div className="text-base font-bold text-emerald-400">0.038 g</div>
              </div>
            </div>
            <div className="p-3 bg-slate-900 rounded font-mono text-[11px] text-slate-300">
              MOTOR-01: ONLINE | SPEED: 65% PWM<br/>
              MPU: X=0.259g, Y=-0.965g, Z=-0.062g<br/>
              IR SENSOR: OBJECT DETECTED (HIGH)
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col justify-center gap-2">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Features & Controls</div>
            <ul className="text-xs text-slate-300 space-y-2">
              <li>✔ <b>Sub-Second Waveforms:</b> Dynamic charts tracking current and vibration over time.</li>
              <li>✔ <b>Remote PWM Control:</b> Live speed modulation and emergency cutoff switch.</li>
              <li>✔ <b>Real-Time Alerts:</b> Automated visual & audible alarms when limits are exceeded.</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 10,
      title: "Project Conclusion & Future Roadmap",
      category: "CONCLUSION & SCOPE",
      badge: "Summary & Roadmap",
      notes: "Conclude by reiterating how edge IoT and ML come together to deliver real-time condition-based intelligence.",
      render: () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">🏁 Project Achievements</div>
            <ul className="text-xs text-slate-300 space-y-1.5">
              <li>✔ End-to-end IoT platform successfully built & tested.</li>
              <li>✔ ESP32 multi-sensor node reliably gathers telemetry.</li>
              <li>✔ FastAPI backend & SQLite database handle live streaming.</li>
              <li>✔ Real-time React dashboard with remote PWM controls.</li>
              <li>✔ Baseline dataset ready for predictive ML models.</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 flex flex-col gap-2">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">🚀 Future Enhancements</div>
            <ul className="text-xs text-slate-300 space-y-1.5">
              <li>• <b>TinyML on Edge:</b> Direct ESP32 neural network inference.</li>
              <li>• <b>Vibration FFT:</b> Harmonic frequency defect analysis.</li>
              <li>• <b>Fleet Scale:</b> Multi-motor node tracking across factories.</li>
              <li>• <b>Mobile App:</b> Push notifications for maintenance teams.</li>
            </ul>
          </div>
        </div>
      )
    }
  ];

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        setCurrentSlide((prev) => Math.min(prev + 1, SLIDES.length - 1));
      } else if (e.key === 'ArrowLeft') {
        setCurrentSlide((prev) => Math.max(prev - 1, 0));
      } else if (e.key.toLowerCase() === 'n') {
        setShowNotes((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [SLIDES.length]);

  return (
    <div className="flex flex-col h-full bg-slate-950 p-6 overflow-hidden">
      {/* Top Bar Controls */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="px-2.5 py-1 text-xs font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 rounded">
            SLIDE {String(currentSlide + 1).padStart(2, '0')} / {String(SLIDES.length).padStart(2, '0')}
          </div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {SLIDES[currentSlide].category}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentSlide((p) => Math.max(p - 1, 0))}
            disabled={currentSlide === 0}
            className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded transition"
          >
            ◀ Prev
          </button>
          <button
            onClick={() => setCurrentSlide((p) => Math.min(p + 1, SLIDES.length - 1))}
            disabled={currentSlide === SLIDES.length - 1}
            className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded transition"
          >
            Next ▶
          </button>
          <button
            onClick={() => setShowNotes((p) => !p)}
            className={`px-3 py-1.5 text-xs font-medium rounded transition ${
              showNotes ? 'bg-cyan-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            📝 Notes
          </button>
          <a
            href="/presentation.html"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-bold text-white bg-sky-600 hover:bg-sky-500 rounded transition flex items-center gap-1.5 shadow-lg shadow-sky-600/30"
          >
            <span>Launch Standalone 25-Slide App ⛶</span>
          </a>
        </div>
      </div>

      {/* Main Slide Card */}
      <div className="flex-1 rounded-2xl bg-slate-900/90 border border-slate-800/80 p-8 shadow-2xl flex flex-col relative overflow-hidden backdrop-blur-md">
        <div className="flex justify-between items-start mb-4 border-b border-slate-800/60 pb-3">
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-cyan-400 mb-1">
              {SLIDES[currentSlide].category}
            </div>
            <h2 className="text-xl font-bold text-white">{SLIDES[currentSlide].title}</h2>
          </div>
          <span className="px-2.5 py-1 text-[11px] font-semibold text-sky-400 bg-sky-950/60 border border-sky-800/60 rounded-full">
            {SLIDES[currentSlide].badge}
          </span>
        </div>

        <div className="flex-1 overflow-y-auto">
          {SLIDES[currentSlide].render()}
        </div>

        {/* Speaker Notes Overlay */}
        {showNotes && (
          <div className="absolute bottom-4 left-6 right-6 p-4 rounded-xl bg-slate-950/95 border border-cyan-500/40 shadow-2xl backdrop-blur-lg">
            <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
              📝 Speaker Notes (Slide {currentSlide + 1})
            </div>
            <p className="text-xs text-slate-200 leading-relaxed">
              {SLIDES[currentSlide].notes}
            </p>
          </div>
        )}
      </div>

      {/* Bottom Progress Bar */}
      <div className="mt-4 flex items-center justify-between text-[11px] text-slate-500">
        <div>Use <b>←/→ Arrow keys</b> or <b>Space</b> to navigate slides</div>
        <div className="w-48 h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-400 to-sky-500 transition-all duration-300"
            style={{ width: `${((currentSlide + 1) / SLIDES.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
