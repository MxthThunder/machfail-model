import { useState } from 'react';

export default function MotorControl({
  motorRunning,
  setMotorRunning,
  commandedSpeed,
  setCommandedSpeed,
}: {
  motorRunning: boolean;
  setMotorRunning: (v: boolean) => void;
  commandedSpeed: number;
  setCommandedSpeed: (v: number) => void;
}) {
  const [confirmEStop, setConfirmEStop] = useState(false);
  const [confirmStop, setConfirmStop] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const actualRpm = motorRunning ? Math.round((commandedSpeed / 100) * 1500 + 50) : 0;
  const actualTemp = motorRunning ? (38 + commandedSpeed * 0.08).toFixed(1) : '--';

  function handleStart() {
    setMotorRunning(true);
    setLastAction(`Motor started at ${new Date().toLocaleTimeString()}`);
  }

  function handleStop() {
    if (confirmStop) {
      setMotorRunning(false);
      setLastAction(`Motor stopped at ${new Date().toLocaleTimeString()}`);
      setConfirmStop(false);
    } else {
      setConfirmStop(true);
      setTimeout(() => setConfirmStop(false), 4000);
    }
  }

  function handleEStop() {
    if (confirmEStop) {
      setMotorRunning(false);
      setCommandedSpeed(0);
      setLastAction(`EMERGENCY STOP activated at ${new Date().toLocaleTimeString()}`);
      setConfirmEStop(false);
    } else {
      setConfirmEStop(true);
      setTimeout(() => setConfirmEStop(false), 5000);
    }
  }

  return (
    <div className="p-6 w-full space-y-5">
      <div>
        <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Motor Control Panel</h2>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          Commands are sent to the ESP32 through the connected network.
        </p>
      </div>

      {/* Status row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Motor Status', value: motorRunning ? 'RUNNING' : 'STOPPED', color: motorRunning ? 'var(--status-online)' : 'var(--status-offline)' },
          { label: 'Actual RPM', value: actualRpm.toLocaleString(), color: 'var(--accent-blue)' },
          { label: 'Temperature', value: `${actualTemp} °C`, color: 'var(--status-warning)' },
          { label: 'Current Draw', value: motorRunning ? `${(commandedSpeed * 0.018 + 0.4).toFixed(2)} A` : '0.00 A', color: 'var(--text-primary)' },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="rounded-lg px-4 py-3"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
          >
            <div className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>{label}</div>
            <div className="font-mono-data text-lg font-bold" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Speed control */}
      <div
        className="rounded-lg p-5 space-y-4"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Speed Control</span>
          <span className="font-mono-data text-xs px-3 py-1 rounded" style={{ background: 'var(--bg-card2)', color: 'var(--accent-blue)' }}>
            {commandedSpeed}% commanded
          </span>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs" style={{ color: 'var(--text-muted)' }}>
            <span>0%</span>
            <span className="font-mono-data text-base font-bold" style={{ color: 'var(--text-primary)' }}>
              {commandedSpeed}%
            </span>
            <span>100%</span>
          </div>
          <div style={{ position: 'relative' }}>
            <div
              className="absolute inset-y-0 left-0 rounded-l-full pointer-events-none"
              style={{ width: `${commandedSpeed}%`, background: 'var(--accent-blue)', opacity: 0.18, top: '50%', transform: 'translateY(-50%)', height: 6 }}
            />
            <input
              type="range"
              min={0}
              max={100}
              value={commandedSpeed}
              onChange={e => setCommandedSpeed(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
          <div className="flex items-center justify-between px-3 py-2 rounded" style={{ background: 'var(--bg-card2)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Commanded Speed</span>
            <span className="font-mono-data font-semibold" style={{ color: 'var(--text-primary)' }}>{commandedSpeed}%</span>
          </div>
          <div className="flex items-center justify-between px-3 py-2 rounded" style={{ background: 'var(--bg-card2)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Actual RPM</span>
            <span className="font-mono-data font-semibold" style={{ color: 'var(--accent-blue)' }}>{actualRpm.toLocaleString()} RPM</span>
          </div>
        </div>
      </div>

      {/* Control buttons */}
      <div
        className="rounded-lg p-5"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="text-xs font-semibold mb-4 uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
          Motor Commands
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {/* Start */}
          <button
            disabled={motorRunning}
            onClick={handleStart}
            className="flex items-center gap-2 px-5 py-2.5 rounded font-semibold text-sm transition-fast"
            style={
              !motorRunning
                ? { background: 'rgba(34,208,110,0.12)', border: '1px solid rgba(34,208,110,0.3)', color: 'var(--status-online)', cursor: 'pointer' }
                : { background: 'var(--bg-card2)', border: '1px solid var(--border-dim)', color: 'var(--text-muted)', cursor: 'not-allowed', opacity: 0.5 }
            }
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Start
          </button>

          {/* Stop */}
          <button
            disabled={!motorRunning}
            onClick={handleStop}
            className="flex items-center gap-2 px-5 py-2.5 rounded font-semibold text-sm transition-fast"
            style={
              motorRunning
                ? confirmStop
                  ? { background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.4)', color: 'var(--status-warning)', cursor: 'pointer' }
                  : { background: 'rgba(43,127,255,0.1)', border: '1px solid rgba(43,127,255,0.25)', color: 'var(--accent-blue)', cursor: 'pointer' }
                : { background: 'var(--bg-card2)', border: '1px solid var(--border-dim)', color: 'var(--text-muted)', cursor: 'not-allowed', opacity: 0.5 }
            }
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12"/></svg>
            {confirmStop ? 'Confirm Stop' : 'Stop'}
          </button>

          {/* Emergency Stop */}
          <button
            onClick={handleEStop}
            className="flex items-center gap-2 px-5 py-2.5 rounded font-bold text-sm transition-fast ml-auto"
            style={
              confirmEStop
                ? { background: 'rgba(240,64,64,0.25)', border: '2px solid rgba(240,64,64,0.7)', color: '#ff6060', cursor: 'pointer', boxShadow: '0 0 16px rgba(240,64,64,0.3)' }
                : { background: 'rgba(240,64,64,0.08)', border: '2px solid rgba(240,64,64,0.35)', color: 'var(--status-critical)', cursor: 'pointer' }
            }
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" fill="currentColor" opacity="0.2" stroke="currentColor" strokeWidth="2"/>
              <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {confirmEStop ? '⚠ CONFIRM E-STOP' : 'Emergency Stop'}
          </button>
        </div>

        {confirmEStop && (
          <div
            className="mt-3 px-3 py-2 rounded text-xs"
            style={{ background: 'rgba(240,64,64,0.06)', border: '1px solid rgba(240,64,64,0.2)', color: 'var(--status-critical)' }}
          >
            Click Emergency Stop again to confirm. This will immediately cut motor power.
          </div>
        )}
      </div>

      {/* Last action log */}
      {lastAction && (
        <div
          className="px-4 py-3 rounded text-xs flex items-center gap-2"
          style={{ background: 'var(--bg-card2)', border: '1px solid var(--border-dim)', color: 'var(--text-muted)' }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          {lastAction}
        </div>
      )}
    </div>
  );
}
