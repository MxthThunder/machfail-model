import { useState, useEffect } from 'react';
import { fetchMotorCondition, fetchMotorStatus, fetchLatestMotorTelemetry } from '../services/api';

type Severity = 'critical' | 'warning' | 'info';

interface Alert {
  id: string;
  severity: Severity;
  machine: string;
  description: string;
  sensor: string;
  value: string;
  time: string;
  status: 'active' | 'acknowledged' | 'resolved';
}

const SEV_CONFIG: Record<Severity, { label: string; color: string; bg: string; border: string }> = {
  critical: { label: 'Critical', color: 'var(--status-critical)', bg: 'rgba(240,64,64,0.06)', border: 'rgba(240,64,64,0.18)' },
  warning:  { label: 'Warning',  color: 'var(--status-warning)',  bg: 'rgba(245,158,11,0.06)', border: 'rgba(245,158,11,0.18)' },
  info:     { label: 'Info',     color: 'var(--accent-blue)',     bg: 'rgba(43,127,255,0.06)', border: 'rgba(43,127,255,0.15)' },
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<Severity | 'all'>('all');

  useEffect(() => {
    let isMounted = true;

    async function evaluateAlerts() {
      const [condition, status, latest] = await Promise.all([
        fetchMotorCondition('M001'),
        fetchMotorStatus('M001'),
        fetchLatestMotorTelemetry('M001'),
      ]);

      if (!isMounted) return;

      const dynamicAlerts: Alert[] = [];

      // 1. Connectivity Alert
      if (status && !status.online) {
        dynamicAlerts.push({
          id: 'esp32-offline',
          severity: 'warning',
          machine: 'MOTOR-01',
          description: 'ESP32 Hardware is currently offline / awaiting Wi-Fi telemetry packet.',
          sensor: 'ESP32 Wi-Fi Comms',
          value: 'OFFLINE',
          time: status.last_seen ? new Date(status.last_seen).toLocaleTimeString() : 'Now',
          status: 'active',
        });
      } else if (status && status.online) {
        dynamicAlerts.push({
          id: 'esp32-online',
          severity: 'info',
          machine: 'MOTOR-01',
          description: `ESP32 Hardware connected successfully. Node IP: ${latest?.esp32_ip || 'Local Network'}`,
          sensor: 'ESP32 Wi-Fi Comms',
          value: 'CONNECTED',
          time: latest?.received_at ? new Date(latest.received_at).toLocaleTimeString() : 'Active',
          status: 'active',
        });
      }

      // 2. Real Condition Alerts
      if (condition) {
        if (condition.temperature.condition === 'HIGH') {
          dynamicAlerts.push({
            id: 'temp-high',
            severity: 'critical',
            machine: 'MOTOR-01',
            description: 'Critical high temperature detected exceeding 40.0°C safety threshold.',
            sensor: 'Temperature (DHT22)',
            value: `${condition.temperature.value.toFixed(1)} °C`,
            time: new Date(condition.timestamp).toLocaleTimeString(),
            status: 'active',
          });
        } else if (condition.temperature.condition === 'MEDIUM') {
          dynamicAlerts.push({
            id: 'temp-med',
            severity: 'warning',
            machine: 'MOTOR-01',
            description: 'Elevated motor temperature in warning zone (35.0–40.0°C).',
            sensor: 'Temperature (DHT22)',
            value: `${condition.temperature.value.toFixed(1)} °C`,
            time: new Date(condition.timestamp).toLocaleTimeString(),
            status: 'active',
          });
        }

        if (condition.rpm.condition === 'HIGH') {
          dynamicAlerts.push({
            id: 'rpm-low',
            severity: 'critical',
            machine: 'MOTOR-01',
            description: 'Low rotational speed sag detected (<500 RPM) indicating mechanical drag or stall.',
            sensor: 'Speed Encoder (IR)',
            value: `${condition.rpm.value.toFixed(1)} RPM`,
            time: new Date(condition.timestamp).toLocaleTimeString(),
            status: 'active',
          });
        }

        if (condition.current.condition === 'HIGH') {
          dynamicAlerts.push({
            id: 'curr-high',
            severity: 'critical',
            machine: 'MOTOR-01',
            description: 'Excessive current draw detected (≥1.50 A). Risk of winding overheating.',
            sensor: 'Current Sensor (ACS712)',
            value: `${condition.current.value.toFixed(2)} A`,
            time: new Date(condition.timestamp).toLocaleTimeString(),
            status: 'active',
          });
        }

        if (condition.vibration.condition === 'HIGH') {
          dynamicAlerts.push({
            id: 'vib-high',
            severity: 'critical',
            machine: 'MOTOR-01',
            description: 'High mechanical vibration detected (>3000 g). Bearing or misalignment fault.',
            sensor: 'Vibration (MPU6050)',
            value: `${condition.vibration.value.toFixed(3)} g`,
            time: new Date(condition.timestamp).toLocaleTimeString(),
            status: 'active',
          });
        }
      }

      setAlerts(dynamicAlerts);
    }

    evaluateAlerts();
    const interval = setInterval(evaluateAlerts, 4000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const critical = alerts.filter((a) => a.severity === 'critical' && a.status === 'active').length;
  const warning = alerts.filter((a) => a.severity === 'warning' && a.status === 'active').length;
  const info = alerts.filter((a) => a.severity === 'info').length;

  const displayed = filter === 'all' ? alerts : alerts.filter((a) => a.severity === filter);

  function acknowledge(id: string) {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, status: 'acknowledged' } : a)));
  }

  function resolve(id: string) {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, status: 'resolved' } : a)));
  }

  return (
    <div className="p-6 space-y-5">
      <div className="flex justify-between items-center flex-wrap gap-2">
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Live Alert Management</h2>
          <p className="text-xs text-slate-400 mt-0.5">Real-time alert dispatch based on actual physical threshold violations</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Critical', count: critical, sev: 'critical' as Severity },
          { label: 'Warning', count: warning, sev: 'warning' as Severity },
          { label: 'Informational', count: info, sev: 'info' as Severity },
        ].map(({ label, count, sev }) => {
          const cfg = SEV_CONFIG[sev];
          return (
            <button
              key={label}
              onClick={() => setFilter(filter === sev ? 'all' : sev)}
              className="rounded-xl px-5 py-4 text-left transition"
              style={{
                background: filter === sev ? cfg.bg : 'var(--bg-card)',
                border: `1px solid ${filter === sev ? cfg.border : 'var(--border-dim)'}`,
              }}
            >
              <div className="text-[10px] uppercase tracking-widest mb-1 font-semibold" style={{ color: 'var(--text-muted)' }}>{label}</div>
              <div className="font-mono text-3xl font-bold" style={{ color: cfg.color }}>{count}</div>
            </button>
          );
        })}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-2 text-xs">
        <span style={{ color: 'var(--text-muted)' }}>Filter:</span>
        {(['all', 'critical', 'warning', 'info'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className="px-3 py-1 rounded-lg capitalize transition font-medium"
            style={
              filter === f
                ? { background: 'var(--accent-blue)', color: '#fff' }
                : { background: 'var(--bg-card)', color: 'var(--text-muted)', border: '1px solid var(--border-dim)' }
            }
          >
            {f}
          </button>
        ))}
      </div>

      {/* Alerts Table */}
      <div
        className="rounded-xl overflow-hidden"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        {displayed.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">
            ✓ No threshold violations detected. All parameters operating within normal baseline limits.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-left uppercase text-[10px] tracking-wider">
                  <th className="p-3">Severity</th>
                  <th className="p-3">Machine</th>
                  <th className="p-3">Description</th>
                  <th className="p-3">Sensor Channel</th>
                  <th className="p-3">Value</th>
                  <th className="p-3">Time</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {displayed.map((alert) => {
                  const cfg = SEV_CONFIG[alert.severity];
                  return (
                    <tr key={alert.id} className="hover:bg-slate-800/30 transition">
                      <td className="p-3">
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                          style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}
                        >
                          {alert.severity}
                        </span>
                      </td>
                      <td className="p-3 font-semibold text-white">{alert.machine}</td>
                      <td className="p-3 text-slate-300">{alert.description}</td>
                      <td className="p-3 text-slate-400">{alert.sensor}</td>
                      <td className="p-3 font-mono font-bold text-white">{alert.value}</td>
                      <td className="p-3 text-slate-400">{alert.time}</td>
                      <td className="p-3">
                        {alert.status === 'active' ? (
                          <div className="flex gap-1.5">
                            <button
                              onClick={() => acknowledge(alert.id)}
                              className="px-2 py-0.5 rounded text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                            >
                              Ack
                            </button>
                            <button
                              onClick={() => resolve(alert.id)}
                              className="px-2 py-0.5 rounded text-[10px] bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-800"
                            >
                              Resolve
                            </button>
                          </div>
                        ) : (
                          <span className="text-[10px] text-slate-500 uppercase font-semibold">{alert.status}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
