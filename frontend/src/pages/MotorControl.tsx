import { useState, useEffect } from 'react';
import {
  sendMotorControl,
  fetchMotorStatus,
  fetchLatestMotorTelemetry,
  connectMotorWebSocket,
  type MotorTelemetryData,
  type MotorStatusData,
} from '../services/api';

export default function MotorControl({
  commandedSpeed,
  setCommandedSpeed,
}: {
  motorRunning?: boolean;
  setMotorRunning?: (v: boolean) => void;
  commandedSpeed: number;
  setCommandedSpeed: (v: number) => void;
}) {
  const [confirmEStop, setConfirmEStop] = useState(false);
  const [confirmStop, setConfirmStop] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [pendingCommand, setPendingCommand] = useState<string | null>(null);
  const [latestTelemetry, setLatestTelemetry] = useState<MotorTelemetryData | null>(null);
  const [motorStatus, setMotorStatus] = useState<MotorStatusData | null>(null);

  // Poll real motor state & connect WebSocket
  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      const [telemetry, status] = await Promise.all([
        fetchLatestMotorTelemetry('M001'),
        fetchMotorStatus('M001'),
      ]);
      if (isMounted) {
        if (telemetry) setLatestTelemetry(telemetry);
        if (status) setMotorStatus(status);
      }
    }

    loadData();

    const ws = connectMotorWebSocket('M001', (payload) => {
      if (isMounted && payload.data) {
        setLatestTelemetry(payload.data);
        if (payload.online !== undefined) {
          setMotorStatus((prev) => (prev ? { ...prev, online: payload.online, status: payload.data.status } : null));
        }
      }
    });

    const pollId = setInterval(loadData, 3000);

    return () => {
      isMounted = false;
      ws.close();
      clearInterval(pollId);
    };
  }, []);

  const isOnline = motorStatus?.online ?? false;
  const actualStatus = latestTelemetry?.status || motorStatus?.status || 'OFF';
  const isActualRunning = actualStatus.toUpperCase() === 'ON';

  async function handleStart() {
    setIsSending(true);
    setPendingCommand('ON');
    try {
      await sendMotorControl('M001', 'ON');
      setLastAction(`ON command dispatched at ${new Date().toLocaleTimeString()}. Awaiting ESP32 hardware execution.`);
    } catch (e: any) {
      setLastAction(`Error dispatching command: ${e.message}`);
    } finally {
      setIsSending(false);
    }
  }

  async function handleStop() {
    if (confirmStop) {
      setIsSending(true);
      setPendingCommand('OFF');
      try {
        await sendMotorControl('M001', 'OFF');
        setLastAction(`OFF command dispatched at ${new Date().toLocaleTimeString()}.`);
      } catch (e: any) {
        setLastAction(`Error dispatching command: ${e.message}`);
      } finally {
        setIsSending(false);
        setConfirmStop(false);
      }
    } else {
      setConfirmStop(true);
      setTimeout(() => setConfirmStop(false), 4000);
    }
  }

  async function handleEStop() {
    if (confirmEStop) {
      setIsSending(true);
      setPendingCommand('OFF');
      setCommandedSpeed(0);
      try {
        await sendMotorControl('M001', 'OFF');
        setLastAction(`EMERGENCY STOP dispatched at ${new Date().toLocaleTimeString()}!`);
      } catch (e: any) {
        setLastAction(`Error during E-Stop: ${e.message}`);
      } finally {
        setIsSending(false);
        setConfirmEStop(false);
      }
    } else {
      setConfirmEStop(true);
      setTimeout(() => setConfirmEStop(false), 5000);
    }
  }

  return (
    <div className="p-6 w-full space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Motor Control Panel</h2>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            Bi-directional motor actuation: Dashboard → FastAPI Command Queue → ESP32 L298N Driver
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider"
            style={{
              background: isOnline ? 'rgba(34,208,110,0.1)' : 'rgba(239,68,68,0.1)',
              border: `1px solid ${isOnline ? 'rgba(34,208,110,0.3)' : 'rgba(239,68,68,0.3)'}`,
              color: isOnline ? 'var(--status-online)' : 'var(--status-critical)',
            }}
          >
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            Hardware: {isOnline ? 'ONLINE (ESP32 Connected)' : 'OFFLINE'}
          </div>
        </div>
      </div>

      {/* Command vs Actual Status Overview Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div
          className="rounded-xl p-4 flex flex-col justify-between"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
        >
          <div className="text-[10px] uppercase tracking-widest text-slate-400">Actual Motor State</div>
          <div className="my-1 font-mono text-xl font-bold" style={{ color: isActualRunning ? 'var(--status-online)' : 'var(--text-muted)' }}>
            {isActualRunning ? 'RUNNING' : 'STOPPED'}
          </div>
          <div className="text-[10px] text-slate-500">Reported by ESP32 Telemetry</div>
        </div>

        <div
          className="rounded-xl p-4 flex flex-col justify-between"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
        >
          <div className="text-[10px] uppercase tracking-widest text-slate-400">Command Requested</div>
          <div className="my-1 font-mono text-xl font-bold text-cyan-400">
            {pendingCommand || 'IDLE'}
          </div>
          <div className="text-[10px] text-slate-500">Backend Queue Status</div>
        </div>

        <div
          className="rounded-xl p-4 flex flex-col justify-between"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
        >
          <div className="text-[10px] uppercase tracking-widest text-slate-400">Actual RPM</div>
          <div className="my-1 font-mono text-xl font-bold text-emerald-400">
            {latestTelemetry ? latestTelemetry.rpm.toFixed(1) : '0.0'} RPM
          </div>
          <div className="text-[10px] text-slate-500">Optical Encoder Feedback</div>
        </div>

        <div
          className="rounded-xl p-4 flex flex-col justify-between"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
        >
          <div className="text-[10px] uppercase tracking-widest text-slate-400">Motor PWM Duty</div>
          <div className="my-1 font-mono text-xl font-bold text-amber-400">
            {latestTelemetry ? `${latestTelemetry.motor_pwm} / 255` : '0 / 255'}
          </div>
          <div className="text-[10px] text-slate-500">L298N Drive Duty Cycle</div>
        </div>
      </div>

      {/* Speed / PWM Control Slider */}
      <div
        className="rounded-xl p-5 space-y-4"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-200">Motor Speed / PWM Command</span>
          <span className="font-mono text-xs px-3 py-1 rounded bg-slate-900 text-cyan-400 border border-slate-800">
            {commandedSpeed}% Command (PWM: {Math.round((commandedSpeed / 100) * 255)} / 255)
          </span>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>0% (0 PWM)</span>
            <span className="font-mono text-base font-bold text-white">
              {commandedSpeed}%
            </span>
            <span>100% (255 PWM)</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={commandedSpeed}
            onChange={(e) => setCommandedSpeed(Number(e.target.value))}
            className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>
      </div>

      {/* Actuation Control Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* START */}
        <button
          onClick={handleStart}
          disabled={isSending}
          className="flex items-center justify-center gap-2 p-4 rounded-xl font-bold text-sm text-emerald-300 bg-emerald-950/40 border border-emerald-800/80 hover:bg-emerald-900/60 active:scale-95 transition disabled:opacity-50"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          {isSending && pendingCommand === 'ON' ? 'Sending ON...' : 'START MOTOR (ON)'}
        </button>

        {/* STOP */}
        <button
          onClick={handleStop}
          disabled={isSending}
          className={`flex items-center justify-center gap-2 p-4 rounded-xl font-bold text-sm transition active:scale-95 disabled:opacity-50 ${
            confirmStop
              ? 'bg-amber-600 text-white border border-amber-500 animate-pulse'
              : 'text-amber-300 bg-amber-950/40 border border-amber-800/80 hover:bg-amber-900/60'
          }`}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <rect x="6" y="6" width="12" height="12" />
          </svg>
          {confirmStop ? 'CONFIRM STOP?' : isSending && pendingCommand === 'OFF' ? 'Stopping...' : 'STOP MOTOR'}
        </button>

        {/* EMERGENCY STOP */}
        <button
          onClick={handleEStop}
          disabled={isSending}
          className={`flex items-center justify-center gap-2 p-4 rounded-xl font-bold text-sm transition active:scale-95 disabled:opacity-50 ${
            confirmEStop
              ? 'bg-red-600 text-white border border-red-500 shadow-red-500/50 shadow-lg animate-pulse'
              : 'text-red-300 bg-red-950/50 border border-red-800/90 hover:bg-red-900/70'
          }`}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          {confirmEStop ? 'CONFIRM EMERGENCY STOP!' : 'EMERGENCY STOP (E-STOP)'}
        </button>
      </div>

      {/* Activity Log Banner */}
      {lastAction && (
        <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-2">
          <span className="text-cyan-400">ℹ️ Log:</span> {lastAction}
        </div>
      )}
    </div>
  );
}
