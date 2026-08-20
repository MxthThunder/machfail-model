import { useState } from 'react';

type Severity = 'critical' | 'warning' | 'info';

interface Alert {
  id: number;
  severity: Severity;
  machine: string;
  description: string;
  sensor: string;
  value: string;
  time: string;
  status: 'active' | 'acknowledged' | 'resolved';
}

const INITIAL_ALERTS: Alert[] = [
  {
    id: 1,
    severity: 'critical',
    machine: 'MOTOR-01',
    description: 'Abnormal motor current detected',
    sensor: 'Current (ACS712)',
    value: '2.8 A',
    time: '08:42:17',
    status: 'active',
  },
  {
    id: 2,
    severity: 'warning',
    machine: 'MOTOR-01',
    description: 'Temperature approaching threshold',
    sensor: 'Temperature (DHT22)',
    value: '58.0 °C',
    time: '09:15:03',
    status: 'active',
  },
  {
    id: 3,
    severity: 'info',
    machine: 'MOTOR-01',
    description: 'Motor started by engineer',
    sensor: 'Motor Control',
    value: '—',
    time: '07:30:00',
    status: 'acknowledged',
  },
  {
    id: 4,
    severity: 'warning',
    machine: 'MOTOR-01',
    description: 'Vibration level elevated above baseline',
    sensor: 'Vibration (MPU6050)',
    value: '0.18 g',
    time: '10:01:44',
    status: 'active',
  },
  {
    id: 5,
    severity: 'info',
    machine: 'MOTOR-01',
    description: 'Scheduled maintenance reminder',
    sensor: 'System',
    value: '—',
    time: '06:00:00',
    status: 'resolved',
  },
  {
    id: 6,
    severity: 'critical',
    machine: 'MOTOR-02',
    description: 'Device offline — no heartbeat received',
    sensor: 'ESP32 Comms',
    value: 'Timeout',
    time: 'Yesterday',
    status: 'active',
  },
];

const SEV_CONFIG: Record<Severity, { label: string; color: string; bg: string; border: string }> = {
  critical: { label: 'Critical', color: 'var(--status-critical)', bg: 'rgba(240,64,64,0.06)', border: 'rgba(240,64,64,0.18)' },
  warning:  { label: 'Warning',  color: 'var(--status-warning)',  bg: 'rgba(245,158,11,0.06)', border: 'rgba(245,158,11,0.18)' },
  info:     { label: 'Info',     color: 'var(--accent-blue)',     bg: 'rgba(43,127,255,0.06)', border: 'rgba(43,127,255,0.15)' },
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>(INITIAL_ALERTS);
  const [filter, setFilter] = useState<Severity | 'all'>('all');

  const critical = alerts.filter(a => a.severity === 'critical' && a.status === 'active').length;
  const warning  = alerts.filter(a => a.severity === 'warning'  && a.status === 'active').length;
  const info     = alerts.filter(a => a.severity === 'info').length;

  const displayed = filter === 'all' ? alerts : alerts.filter(a => a.severity === filter);

  function acknowledge(id: number) {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a));
  }
  function resolve(id: number) {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'resolved' } : a));
  }

  return (
    <div className="p-6 space-y-5">
      <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Alert Management</h2>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Critical', count: critical, sev: 'critical' as Severity },
          { label: 'Warning',  count: warning,  sev: 'warning'  as Severity },
          { label: 'Informational', count: info, sev: 'info'    as Severity },
        ].map(({ label, count, sev }) => {
          const cfg = SEV_CONFIG[sev];
          return (
            <button
              key={label}
              onClick={() => setFilter(filter === sev ? 'all' : sev)}
              className="rounded-lg px-5 py-4 text-left transition-fast"
              style={{
                background: filter === sev ? cfg.bg : 'var(--bg-card)',
                border: `1px solid ${filter === sev ? cfg.border : 'var(--border-dim)'}`,
              }}
            >
              <div className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>{label}</div>
              <div className="font-mono-data text-3xl font-bold" style={{ color: cfg.color }}>{count}</div>
            </button>
          );
        })}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-2 text-xs">
        <span style={{ color: 'var(--text-muted)' }}>Filter:</span>
        {(['all', 'critical', 'warning', 'info'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className="px-2.5 py-1 rounded capitalize transition-fast"
            style={
              filter === f
                ? { background: 'rgba(43,127,255,0.12)', color: 'var(--accent-blue)', border: '1px solid rgba(43,127,255,0.25)' }
                : { color: 'var(--text-muted)', border: '1px solid var(--border-dim)' }
            }
          >
            {f}
          </button>
        ))}
        <span className="ml-auto font-mono-data" style={{ color: 'var(--text-muted)' }}>
          {displayed.length} alerts
        </span>
      </div>

      {/* Alert list */}
      <div className="space-y-2">
        {displayed.map(alert => {
          const cfg = SEV_CONFIG[alert.severity];
          return (
            <div
              key={alert.id}
              className="rounded-lg px-4 py-3 flex items-start gap-4"
              style={{
                background: 'var(--bg-card)',
                border: `1px solid var(--border-dim)`,
                opacity: alert.status === 'resolved' ? 0.5 : 1,
              }}
            >
              {/* Severity indicator */}
              <div className="flex flex-col items-center gap-1 pt-0.5 shrink-0">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: cfg.color }} />
                <div
                  className="text-[9px] uppercase font-semibold tracking-widest"
                  style={{ color: cfg.color, writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}
                >
                  {cfg.label}
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {alert.description}
                  </span>
                  <StatusChip status={alert.status} />
                </div>
                <div className="flex items-center gap-4 mt-1.5 text-[11px] flex-wrap" style={{ color: 'var(--text-muted)' }}>
                  <span>
                    <span className="font-mono-data" style={{ color: 'var(--accent-blue)' }}>{alert.machine}</span>
                  </span>
                  <span>{alert.sensor}</span>
                  {alert.value !== '—' && (
                    <span className="font-mono-data" style={{ color: cfg.color }}>{alert.value}</span>
                  )}
                  <span className="font-mono-data">{alert.time}</span>
                </div>
              </div>

              {/* Actions */}
              {alert.status === 'active' && (
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => acknowledge(alert.id)}
                    className="text-[10px] px-2.5 py-1 rounded transition-fast"
                    style={{ background: 'var(--bg-card2)', border: '1px solid var(--border-mid)', color: 'var(--text-muted)' }}
                  >
                    Ack
                  </button>
                  <button
                    onClick={() => resolve(alert.id)}
                    className="text-[10px] px-2.5 py-1 rounded transition-fast"
                    style={{ background: 'rgba(34,208,110,0.08)', border: '1px solid rgba(34,208,110,0.2)', color: 'var(--status-online)' }}
                  >
                    Resolve
                  </button>
                </div>
              )}
              {alert.status === 'acknowledged' && (
                <button
                  onClick={() => resolve(alert.id)}
                  className="text-[10px] px-2.5 py-1 rounded transition-fast shrink-0"
                  style={{ background: 'rgba(34,208,110,0.08)', border: '1px solid rgba(34,208,110,0.2)', color: 'var(--status-online)' }}
                >
                  Resolve
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatusChip({ status }: { status: Alert['status'] }) {
  const styles: Record<Alert['status'], { color: string; bg: string; border: string; label: string }> = {
    active:       { label: 'Active',       color: 'var(--status-critical)', bg: 'rgba(240,64,64,0.08)',    border: 'rgba(240,64,64,0.2)' },
    acknowledged: { label: 'Acknowledged', color: 'var(--status-warning)',  bg: 'rgba(245,158,11,0.08)',   border: 'rgba(245,158,11,0.2)' },
    resolved:     { label: 'Resolved',     color: 'var(--status-online)',   bg: 'rgba(34,208,110,0.08)',   border: 'rgba(34,208,110,0.2)' },
  };
  const s = styles[status];
  return (
    <span
      className="text-[9px] px-2 py-0.5 rounded uppercase font-semibold tracking-wider shrink-0"
      style={{ background: s.bg, border: `1px solid ${s.border}`, color: s.color }}
    >
      {s.label}
    </span>
  );
}
