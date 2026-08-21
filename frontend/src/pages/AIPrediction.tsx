import { useState, useEffect } from 'react';
import {
  fetchMotorCondition,
  analyzeMotorCondition,
  connectMotorWebSocket,
  fetchMotorStatus,
  type MotorConditionAnalysis,
} from '../services/api';

type OperatingMode = 'live' | 'simulation';

export default function AIPrediction({ motorRunning }: { motorRunning: boolean }) {
  const [operatingMode, setOperatingMode] = useState<OperatingMode>('live');

  // Live Mode State
  const [liveCondition, setLiveCondition] = useState<MotorConditionAnalysis | null>(null);
  const [isHardwareOnline, setIsHardwareOnline] = useState<boolean>(false);
  const [lastTelemetryTime, setLastTelemetryTime] = useState<string | null>(null);

  // Simulation Mode State
  const [simTemp, setSimTemp] = useState<string>('32.0');
  const [simRpm, setSimRpm] = useState<string>('1400');
  const [simCurrent, setSimCurrent] = useState<string>('0.50');
  const [simVibration, setSimVibration] = useState<string>('1000');
  const [simResult, setSimResult] = useState<MotorConditionAnalysis | null>(null);
  const [simError, setSimError] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Load live condition on mount and listen to WebSocket
  useEffect(() => {
    let isMounted = true;

    async function loadLiveTelemetry() {
      const [condition, status] = await Promise.all([
        fetchMotorCondition('M001'),
        fetchMotorStatus('M001'),
      ]);
      if (isMounted) {
        if (condition) {
          setLiveCondition(condition);
          setLastTelemetryTime(condition.timestamp);
        }
        if (status) {
          setIsHardwareOnline(status.online);
        }
      }
    }

    loadLiveTelemetry();

    // WebSocket real-time subscription for live ESP32 data
    const ws = connectMotorWebSocket('M001', (payload) => {
      if (isMounted) {
        if (payload.condition) {
          setLiveCondition(payload.condition);
          setLastTelemetryTime(payload.condition.timestamp);
        }
        if (payload.online !== undefined) {
          setIsHardwareOnline(payload.online);
        }
      }
    });

    const pollId = setInterval(loadLiveTelemetry, 3000);

    return () => {
      isMounted = false;
      ws.close();
      clearInterval(pollId);
    };
  }, []);

  // Validation & Analysis for Simulation Mode
  async function handleRunSimulation() {
    setSimError(null);

    // Validation
    const t = parseFloat(simTemp.trim());
    const r = parseFloat(simRpm.trim());
    const c = parseFloat(simCurrent.trim());
    const v = parseFloat(simVibration.trim());

    if (isNaN(t) || simTemp.trim() === '') {
      setSimError('Please enter a valid numeric value for Temperature (°C).');
      return;
    }
    if (isNaN(r) || simRpm.trim() === '' || r < 0) {
      setSimError('Please enter a valid non-negative number for RPM.');
      return;
    }
    if (isNaN(c) || simCurrent.trim() === '' || c < 0) {
      setSimError('Please enter a valid non-negative number for Current (A).');
      return;
    }
    if (isNaN(v) || simVibration.trim() === '' || v < 0) {
      setSimError('Please enter a valid non-negative number for Vibration (g).');
      return;
    }

    setIsSimulating(true);

    try {
      // Calls the EXACT same condition-analysis service on the backend
      const result = await analyzeMotorCondition({
        motor_id: 'M001-SIMULATED',
        temperature: t,
        rpm: r,
        current: c,
        vibration: v,
      });
      setSimResult(result);
    } catch (err: any) {
      setSimError(`Simulation Analysis Error: ${err.message}`);
    } finally {
      setIsSimulating(false);
    }
  }

  const activeDisplay = operatingMode === 'live' ? liveCondition : simResult;
  const isCurrentlyProcessing = operatingMode === 'simulation' && isSimulating;

  const getConditionColor = (cond?: string) => {
    switch (cond) {
      case 'NORMAL':
        return '#22d06e';
      case 'MEDIUM':
        return '#f59e0b';
      case 'HIGH':
        return '#ef4444';
      default:
        return 'var(--text-muted)';
    }
  };

  const getConditionBg = (cond?: string) => {
    switch (cond) {
      case 'NORMAL':
        return 'rgba(34,208,110,0.08)';
      case 'MEDIUM':
        return 'rgba(245,158,11,0.08)';
      case 'HIGH':
        return 'rgba(239,68,68,0.08)';
      default:
        return 'rgba(100,116,139,0.08)';
    }
  };

  return (
    <div className="p-6 w-full space-y-6">
      {/* Operating Mode Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">
            OPERATING MODE SELECTOR
          </div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white">Motor Condition & Failure Risk</h2>
            {operatingMode === 'live' ? (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-950/80 text-emerald-300 border border-emerald-700">
                MODE: LIVE HARDWARE | Source: ESP32
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-950/80 text-purple-300 border border-purple-700">
                MODE: SIMULATION | Source: Manual Input
              </span>
            )}
          </div>
        </div>

        {/* Mode Toggle Buttons */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800 self-stretch sm:self-auto">
          <button
            onClick={() => setOperatingMode('live')}
            className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              operatingMode === 'live'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isHardwareOnline ? 'bg-white animate-pulse' : 'bg-slate-400'}`} />
            [ LIVE HARDWARE ]
          </button>
          <button
            onClick={() => {
              setOperatingMode('simulation');
              if (!simResult) handleRunSimulation();
            }}
            className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              operatingMode === 'simulation'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>⚙️</span>
            [ SIMULATION ]
          </button>
        </div>
      </div>

      {/* Mode Specific Context Notice */}
      {operatingMode === 'live' ? (
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <span className={`w-2 h-2 rounded-full ${isHardwareOnline ? 'bg-emerald-400' : 'bg-red-400'}`} />
            <span>ESP32 Hardware: <b>{isHardwareOnline ? 'CONNECTED & STREAMING' : 'OFFLINE (Awaiting Telemetry)'}</b></span>
            {lastTelemetryTime && (
              <span className="text-slate-500 ml-2">Last Update: {new Date(lastTelemetryTime).toLocaleTimeString()}</span>
            )}
          </div>
          <span className="font-mono text-[11px] text-slate-400">Endpoint: POST /api/motor/data</span>
        </div>
      ) : (
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-purple-950/30 border border-purple-800/40 text-xs text-purple-200">
          <div className="flex items-center gap-2">
            <span>🛡️</span>
            <span><b>Simulation Mode Isolated:</b> Manual inputs will NOT alter the physical motor or overwrite real ESP32 telemetry.</span>
          </div>
          <span className="font-bold text-purple-400 text-[11px]">SIMULATION RESULT</span>
        </div>
      )}

      {/* 3 Pipeline Stages */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Pipeline Stages:
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full md:w-auto flex-1 max-w-3xl">
          <StageBadge title="1. Sensor Data Analysis" status={isCurrentlyProcessing ? '⟳ Processing...' : '✓ Complete'} isComplete={!isCurrentlyProcessing} />
          <StageBadge title="2. Motor Condition Analysis" status={isCurrentlyProcessing ? '⟳ Processing...' : '✓ Complete'} isComplete={!isCurrentlyProcessing} />
          <StageBadge title="3. Failure Risk Analysis" status={isCurrentlyProcessing ? '⟳ Processing...' : '✓ Complete'} isComplete={!isCurrentlyProcessing} />
        </div>
      </div>

      {/* Simulation Input Panel (Visible ONLY in Simulation Mode) */}
      {operatingMode === 'simulation' && (
        <div className="p-5 rounded-2xl bg-slate-900 border border-purple-800/50 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
            <div>
              <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🎛️</span> SIMULATION MODE INPUT PANEL
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Manually enter the four sensor parameters to evaluate with the reusable condition-analysis engine.
              </p>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => { setSimTemp('32.0'); setSimRpm('1500'); setSimCurrent('0.50'); setSimVibration('1000'); }}
                className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded text-emerald-300 font-semibold border border-slate-700 transition"
              >
                Test 1 (Normal)
              </button>
              <button
                onClick={() => { setSimTemp('37.0'); setSimRpm('800'); setSimCurrent('1.20'); setSimVibration('2500'); }}
                className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded text-amber-300 font-semibold border border-slate-700 transition"
              >
                Test 2 (Medium)
              </button>
              <button
                onClick={() => { setSimTemp('42.0'); setSimRpm('300'); setSimCurrent('1.70'); setSimVibration('3500'); }}
                className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded text-red-300 font-semibold border border-slate-700 transition"
              >
                Test 3 (High)
              </button>
              <button
                onClick={() => { setSimTemp('32.9'); setSimRpm('1340.7'); setSimCurrent('0.00'); setSimVibration('0.035'); }}
                className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded text-cyan-300 font-semibold border border-slate-700 transition"
              >
                Test 4 (Baseline)
              </button>
              <button
                onClick={() => { setSimTemp('36.0'); setSimRpm('1400'); setSimCurrent('0.80'); setSimVibration('1000'); }}
                className="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded text-purple-300 font-semibold border border-slate-700 transition"
              >
                Test 5 (Temp Med)
              </button>
            </div>
          </div>

          {/* Validation Error message */}
          {simError && (
            <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2">
              <span>⚠️</span>
              <span>{simError}</span>
            </div>
          )}

          {/* Inputs Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="space-y-1">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>Temperature (°C)</span>
                <span className="text-slate-500 text-[10px]">30–45°C</span>
              </label>
              <input
                type="text"
                value={simTemp}
                onChange={(e) => setSimTemp(e.target.value)}
                placeholder="e.g. 32.0"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 font-mono text-white focus:border-purple-500 outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>RPM (Speed)</span>
                <span className="text-slate-500 text-[10px]">&gt;1000 norm</span>
              </label>
              <input
                type="text"
                value={simRpm}
                onChange={(e) => setSimRpm(e.target.value)}
                placeholder="e.g. 1400"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 font-mono text-white focus:border-purple-500 outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>Current (A)</span>
                <span className="text-slate-500 text-[10px]">&lt;1.0A norm</span>
              </label>
              <input
                type="text"
                value={simCurrent}
                onChange={(e) => setSimCurrent(e.target.value)}
                placeholder="e.g. 0.50"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 font-mono text-white focus:border-purple-500 outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>Vibration (g)</span>
                <span className="text-slate-500 text-[10px]">≤2000g norm</span>
              </label>
              <input
                type="text"
                value={simVibration}
                onChange={(e) => setSimVibration(e.target.value)}
                placeholder="e.g. 1000"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 font-mono text-white focus:border-purple-500 outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="w-full py-3 bg-purple-600 hover:bg-purple-500 font-bold text-xs rounded-xl text-white shadow-lg transition active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <span>{isSimulating ? '⟳ Calculating Analysis...' : '▶ RUN CONDITION ANALYSIS (ANALYZE)'}</span>
          </button>
        </div>
      )}

      {/* Main Condition & Risk Results Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Overall Condition & Score Card */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                OVERALL MOTOR CONDITION
              </span>
              <span className="text-[10px] font-mono text-slate-400 px-2 py-0.5 rounded bg-slate-950">
                {operatingMode === 'live' ? 'LIVE ESP32' : 'SIMULATED'}
              </span>
            </div>

            <div
              className="p-5 rounded-xl border text-center my-3 transition"
              style={{
                background: getConditionBg(activeDisplay?.overall_condition),
                borderColor: `${getConditionColor(activeDisplay?.overall_condition)}44`,
              }}
            >
              <div
                className="text-3xl font-extrabold tracking-wider"
                style={{ color: getConditionColor(activeDisplay?.overall_condition) }}
              >
                {activeDisplay?.overall_condition || 'NORMAL'}
              </div>
              <div className="text-xs text-slate-300 mt-1.5 font-medium">
                {activeDisplay?.message || 'Motor operating normally'}
              </div>
            </div>

            {/* Score & Risk Indicators */}
            <div className="space-y-3 mt-4 text-xs">
              <div className="flex justify-between items-center py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Condition Score:</span>
                <span className="font-mono text-base font-bold text-white">
                  {activeDisplay?.condition_score ?? 0} / {activeDisplay?.maximum_score ?? 8}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Failure Risk:</span>
                <span
                  className="font-bold px-2.5 py-0.5 rounded text-xs uppercase"
                  style={{
                    color: getConditionColor(activeDisplay?.failure_risk),
                    background: getConditionBg(activeDisplay?.failure_risk),
                    border: `1px solid ${getConditionColor(activeDisplay?.failure_risk)}44`,
                  }}
                >
                  {activeDisplay?.failure_risk || 'LOW'}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-slate-400 font-medium">Assessment Method:</span>
                <span className="font-mono text-[11px] text-cyan-400 font-semibold">
                  RULE-BASED FAILURE RISK
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[10px] text-slate-500">
            * Evaluated using the unified condition engine with zero artificial percentage claims.
          </div>
        </div>

        {/* Center & Right: 4 Physical Parameter Classification Cards */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
              PARAMETER EVALUATION BREAKDOWN
            </span>
            <span className="text-[11px] text-slate-500">
              Priority: HIGH &gt; MEDIUM &gt; NORMAL
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {/* Temperature */}
            <ParameterCard
              title="Temperature"
              value={activeDisplay?.temperature?.value ?? (operatingMode === 'live' ? 0 : parseFloat(simTemp) || 0)}
              unit="°C"
              condition={activeDisplay?.temperature?.condition ?? 'NORMAL'}
              score={activeDisplay?.temperature?.score ?? 0}
              rule="30–35°C Norm | 35–40°C Med | 40–45°C High"
              color={getConditionColor(activeDisplay?.temperature?.condition)}
            />

            {/* RPM */}
            <ParameterCard
              title="RPM (Shaft Speed)"
              value={activeDisplay?.rpm?.value ?? (operatingMode === 'live' ? 0 : parseFloat(simRpm) || 0)}
              unit="RPM"
              condition={activeDisplay?.rpm?.condition ?? 'NORMAL'}
              score={activeDisplay?.rpm?.score ?? 0}
              rule="&gt;1000 Norm | 500–1000 Med | &lt;500 High"
              color={getConditionColor(activeDisplay?.rpm?.condition)}
            />

            {/* Current */}
            <ParameterCard
              title="Current Draw"
              value={activeDisplay?.current?.value ?? (operatingMode === 'live' ? 0 : parseFloat(simCurrent) || 0)}
              unit="A"
              condition={activeDisplay?.current?.condition ?? 'NORMAL'}
              score={activeDisplay?.current?.score ?? 0}
              rule="&lt;1.0A Norm | 1.0–1.5A Med | ≥1.5A High"
              color={getConditionColor(activeDisplay?.current?.condition)}
            />

            {/* Vibration */}
            <ParameterCard
              title="Vibration"
              value={activeDisplay?.vibration?.value ?? (operatingMode === 'live' ? 0 : parseFloat(simVibration) || 0)}
              unit="g"
              condition={activeDisplay?.vibration?.condition ?? 'NORMAL'}
              score={activeDisplay?.vibration?.score ?? 0}
              rule="≤2000g Norm | 2000–3000g Med | &gt;3000g High"
              color={getConditionColor(activeDisplay?.vibration?.condition)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StageBadge({ title, status, isComplete }: { title: string; status: string; isComplete: boolean }) {
  return (
    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between">
      <span className="text-[11px] font-medium text-slate-300">{title}</span>
      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${isComplete ? 'text-emerald-400 bg-emerald-950/60' : 'text-amber-400 bg-amber-950/60'}`}>
        {status}
      </span>
    </div>
  );
}

function ParameterCard({
  title,
  value,
  unit,
  condition,
  score,
  rule,
  color,
}: {
  title: string;
  value: number;
  unit: string;
  condition: string;
  score: number;
  rule: string;
  color: string;
}) {
  return (
    <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold text-slate-400">{title}</span>
        <span
          className="font-bold text-[10px] px-2 py-0.5 rounded uppercase tracking-wider"
          style={{ color: color, background: `${color}18`, border: `1px solid ${color}33` }}
        >
          {condition}
        </span>
      </div>

      <div className="my-2">
        <span className="font-mono text-2xl font-bold text-white">
          {typeof value === 'number' ? value.toFixed(unit === '°C' ? 1 : unit === 'RPM' ? 1 : 2) : value}
        </span>
        <span className="ml-1 text-xs text-slate-400">{unit}</span>
      </div>

      <div className="flex justify-between items-center text-[10px] text-slate-500 pt-2 border-t border-slate-800/80">
        <span>Score: <b className="text-slate-300">{score} / 2</b></span>
        <span className="truncate max-w-[150px]">{rule}</span>
      </div>
    </div>
  );
}
