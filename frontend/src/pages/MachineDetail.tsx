import { useState, useEffect, useRef } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  fetchLatestMotorTelemetry,
  fetchMotorStatus,
  connectMotorWebSocket,
  MotorTelemetryData,
} from '../services/api';

type Metric = 'rpm' | 'temperature' | 'current' | 'vibration' | 'humidity' | 'total_acceleration';
type TimeRange = '1m' | '5m' | '1h' | '24h';

const METRIC_CONFIG: Record<Metric, { label: string; unit: string; color: string }> = {
  rpm:                { label: 'RPM',                unit: 'RPM', color: '#2b7fff' },
  temperature:        { label: 'Temperature',        unit: '°C',  color: '#f59e0b' },
  current:            { label: 'Current',            unit: 'A',   color: '#a78bfa' },
  vibration:          { label: 'Vibration',          unit: 'g',   color: '#22d06e' },
  humidity:           { label: 'Humidity',           unit: '%',   color: '#06b6d4' },
  total_acceleration: { label: 'Total Acceleration', unit: 'g',   color: '#f43f5e' },
};

const TIME_RANGES: { key: TimeRange; label: string; points: number }[] = [
  { key: '1m',  label: '1 Min',  points: 60  },
  { key: '5m',  label: '5 Min',  points: 60  },
  { key: '1h',  label: '1 Hour', points: 60  },
  { key: '24h', label: '24 Hours', points: 72 },
];

export default function MachineDetail({
  onBack,
}: {
  motorRunning?: boolean;
  onBack: () => void;
}) {
  const [metric, setMetric] = useState<Metric>('rpm');
  const [timeRange, setTimeRange] = useState<TimeRange>('5m');
  const [realTelemetry, setRealTelemetry] = useState<MotorTelemetryData | null>(null);
  const [isHardwareOnline, setIsHardwareOnline] = useState<boolean>(false);
  const [lastReceivedAt, setLastReceivedAt] = useState<string | null>(null);
  const [chartData, setChartData] = useState<{ i: number; value: number }[]>([]);
  const tickRef = useRef(0);

  // Initial fetch and WebSocket connection for real ESP32 telemetry
  useEffect(() => {
    let isMounted = true;

    async function loadInitial() {
      const [latest, status] = await Promise.all([
        fetchLatestMotorTelemetry('M001'),
        fetchMotorStatus('M001'),
      ]);
      if (isMounted) {
        if (latest) {
          setRealTelemetry(latest);
          setLastReceivedAt(latest.received_at || latest.timestamp || new Date().toISOString());
        }
        if (status) {
          setIsHardwareOnline(status.online);
        }
      }
    }

    loadInitial();

    // WebSocket real-time listener
    const ws = connectMotorWebSocket('M001', (payload) => {
      if (isMounted && payload.data) {
        setRealTelemetry(payload.data);
        setIsHardwareOnline(payload.online ?? true);
        setLastReceivedAt(payload.data.received_at || new Date().toISOString());
      }
    });

    // Fallback polling every 3 seconds if WebSocket is closed
    const pollId = setInterval(async () => {
      const [latest, status] = await Promise.all([
        fetchLatestMotorTelemetry('M001'),
        fetchMotorStatus('M001'),
      ]);
      if (isMounted) {
        if (latest) setRealTelemetry(latest);
        if (status) setIsHardwareOnline(status.online);
      }
    }, 3000);

    return () => {
      isMounted = false;
      ws.close();
      clearInterval(pollId);
    };
  }, []);

  // Update chart when telemetry or metric changes
  useEffect(() => {
    if (!realTelemetry) return;
    const val = Number(realTelemetry[metric as keyof MotorTelemetryData]) || 0;
    tickRef.current++;
    setChartData((prev) => {
      const t = TIME_RANGES.find((r) => r.key === timeRange)!;
      const next = [...prev.slice(-(t.points - 1)), { i: tickRef.current, value: parseFloat(val.toFixed(2)) }];
      return next;
    });
  }, [realTelemetry, metric, timeRange]);

  const cfg = METRIC_CONFIG[metric];
  const latestChartValue = chartData[chartData.length - 1]?.value ?? (realTelemetry ? Number(realTelemetry[metric as keyof MotorTelemetryData]) : 0);

  const getVibrationColor = (level?: string) => {
    switch (level?.toUpperCase()) {
      case 'LOW':
        return '#22d06e';
      case 'MEDIUM':
        return '#f59e0b';
      case 'HIGH':
        return '#ef4444';
      default:
        return 'var(--text-muted)';
    }
  };

  return (
    <div className="p-6 space-y-5">
      {/* Back + Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs mb-2 transition-fast hover:opacity-80"
            style={{ color: 'var(--text-muted)' }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Back to Machines
          </button>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>MOTOR-01 (M001)</h2>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Industrial DC Motor Node</span>
            <StatusBadge running={isHardwareOnline && realTelemetry?.status === 'ON'} online={isHardwareOnline} hasData={realTelemetry !== null} />
          </div>
        </div>
        <div className="text-right text-xs space-y-0.5">
          <div style={{ color: 'var(--text-muted)' }}>ESP32 IP: <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{realTelemetry?.esp32_ip || 'Not Connected'}</span></div>
          <div style={{ color: 'var(--text-muted)' }}>Last Telemetry: <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{lastReceivedAt ? new Date(lastReceivedAt).toLocaleTimeString() : 'Awaiting data'}</span></div>
        </div>
      </div>

      {/* Connection Notice */}
      {!realTelemetry && (
        <div
          className="flex items-center justify-between px-4 py-3 rounded-lg text-xs"
          style={{ background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.25)', color: 'var(--accent-blue)' }}
        >
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span><b>Awaiting Real ESP32 Hardware:</b> Power on the ESP32 and send live telemetry to <code>POST /api/motor/data</code>.</span>
          </div>
          <span className="font-mono text-[11px]">http://localhost:8000/api/motor/data</span>
        </div>
      )}

      {/* Grid of All Real Sensor Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {/* RPM */}
        <SensorCard
          label="RPM"
          value={realTelemetry ? realTelemetry.rpm.toFixed(1) : '---'}
          unit="RPM"
          icon={<IconGauge />}
          isLive={isHardwareOnline}
          subtext={`Pulses: ${realTelemetry ? realTelemetry.ir_pulses : 0}`}
        />

        {/* Temperature */}
        <SensorCard
          label="Temperature"
          value={realTelemetry ? realTelemetry.temperature.toFixed(1) : '---'}
          unit="°C"
          icon={<IconThermo />}
          isLive={isHardwareOnline}
          subtext="DHT22 Sensor"
        />

        {/* Humidity */}
        <SensorCard
          label="Humidity"
          value={realTelemetry ? realTelemetry.humidity.toFixed(1) : '---'}
          unit="%"
          icon={<IconDroplet />}
          isLive={isHardwareOnline}
          subtext="Ambient RH"
        />

        {/* Current */}
        <SensorCard
          label="Current"
          value={realTelemetry ? realTelemetry.current.toFixed(2) : '---'}
          unit="A"
          icon={<IconZap />}
          isLive={isHardwareOnline}
          subtext={`ADC: ${realTelemetry ? realTelemetry.acs_adc : 0}`}
        />

        {/* Vibration Level */}
        <SensorCard
          label="Vibration"
          value={realTelemetry ? `${realTelemetry.vibration.toFixed(2)} g` : '---'}
          unit=""
          icon={<IconWave />}
          isLive={isHardwareOnline}
          badge={realTelemetry?.vibration_level}
          badgeColor={getVibrationColor(realTelemetry?.vibration_level)}
          subtext={`Level: ${realTelemetry ? realTelemetry.vibration_level : '---'}`}
        />

        {/* Motor PWM / State */}
        <SensorCard
          label="Motor PWM"
          value={realTelemetry ? `${realTelemetry.motor_pwm} / 255` : '---'}
          unit=""
          icon={<IconSliders />}
          isLive={isHardwareOnline}
          subtext={`Status: ${realTelemetry?.status || 'OFF'}`}
        />
      </div>

      {/* Detailed Diagnostics: MPU 3-Axis & IR Sensor */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">📐 MPU6050 3-Axis Acceleration</div>
          <div className="grid grid-cols-3 gap-2 text-center my-1 font-mono text-xs">
            <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">X-Axis</div>
              <div className="font-bold text-white mt-0.5">{realTelemetry ? `${realTelemetry.mpu_x.toFixed(3)} g` : '---'}</div>
            </div>
            <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Y-Axis</div>
              <div className="font-bold text-white mt-0.5">{realTelemetry ? `${realTelemetry.mpu_y.toFixed(3)} g` : '---'}</div>
            </div>
            <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Z-Axis</div>
              <div className="font-bold text-white mt-0.5">{realTelemetry ? `${realTelemetry.mpu_z.toFixed(3)} g` : '---'}</div>
            </div>
          </div>
          <div className="text-[11px] text-slate-400 flex justify-between mt-2 pt-2 border-t border-slate-800/80">
            <span>Total Accel: <b className="text-white">{realTelemetry ? `${realTelemetry.total_acceleration.toFixed(3)} g` : '---'}</b></span>
            <span>Vibration: <b className="text-emerald-400">{realTelemetry ? `${realTelemetry.vibration.toFixed(3)} g` : '---'}</b></span>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="text-xs font-bold text-sky-400 uppercase tracking-wider mb-2">👁️ Optical IR & Speed Encoder</div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center py-1 border-b border-slate-800">
              <span className="text-slate-400">IR State:</span>
              <span className="font-mono font-bold text-white">{realTelemetry ? (realTelemetry.ir === 0 ? 'LOW (Beam Broken / Detected)' : 'HIGH') : '---'}</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-800">
              <span className="text-slate-400">Cumulative IR Pulses:</span>
              <span className="font-mono font-bold text-cyan-400">{realTelemetry ? realTelemetry.ir_pulses : '---'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Calculated RPM:</span>
              <span className="font-mono font-bold text-emerald-400">{realTelemetry ? `${realTelemetry.rpm.toFixed(1)} RPM` : '---'}</span>
            </div>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">⚡ Electrical Current & Actuation</div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center py-1 border-b border-slate-800">
              <span className="text-slate-400">ACS712 ADC Count:</span>
              <span className="font-mono font-bold text-white">{realTelemetry ? realTelemetry.acs_adc : '---'}</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-800">
              <span className="text-slate-400">Motor Current:</span>
              <span className="font-mono font-bold text-amber-400">{realTelemetry ? `${realTelemetry.current.toFixed(2)} A` : '---'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">L298N PWM Duty:</span>
              <span className="font-mono font-bold text-white">{realTelemetry ? `${realTelemetry.motor_pwm} / 255` : '---'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Live Waveform Chart */}
      <div
        className="rounded-lg p-5"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full pulse-dot" style={{ background: cfg.color }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Real-Time Waveform: {cfg.label}
            </span>
            <span className="font-mono-data text-xs px-2 py-0.5 rounded" style={{ background: 'var(--bg-card2)', color: cfg.color }}>
              {latestChartValue} {cfg.unit}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Metric selector */}
            <div className="flex gap-1 p-1 rounded" style={{ background: 'var(--bg-card2)' }}>
              {(Object.keys(METRIC_CONFIG) as Metric[]).map((m) => (
                <button
                  key={m}
                  onClick={() => setMetric(m)}
                  className="px-2.5 py-1 rounded text-[11px] font-medium transition-fast"
                  style={
                    metric === m
                      ? { background: METRIC_CONFIG[m].color + '22', color: METRIC_CONFIG[m].color, border: `1px solid ${METRIC_CONFIG[m].color}44` }
                      : { color: 'var(--text-muted)', border: '1px solid transparent' }
                  }
                >
                  {METRIC_CONFIG[m].label}
                </button>
              ))}
            </div>

            {/* Time range */}
            <div className="flex gap-1 p-1 rounded" style={{ background: 'var(--bg-card2)' }}>
              {TIME_RANGES.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTimeRange(t.key)}
                  className="px-2.5 py-1 rounded text-[11px] font-medium transition-fast"
                  style={
                    timeRange === t.key
                      ? { background: 'rgba(43,127,255,0.15)', color: 'var(--accent-blue)', border: '1px solid rgba(43,127,255,0.25)' }
                      : { color: 'var(--text-muted)', border: '1px solid transparent' }
                  }
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData.length > 0 ? chartData : [{ i: 0, value: 0 }]} margin={{ top: 5, right: 8, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={cfg.color} stopOpacity={0.25} />
                <stop offset="95%" stopColor={cfg.color} stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(29,51,84,0.6)" vertical={false} />
            <XAxis dataKey="i" hide />
            <YAxis
              domain={['auto', 'auto']}
              tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card2)', border: '1px solid var(--border-mid)', borderRadius: 6 }}
              labelStyle={{ display: 'none' }}
              itemStyle={{ color: cfg.color, fontFamily: 'JetBrains Mono', fontSize: 12 }}
              formatter={(v) => [`${v} ${cfg.unit}`, cfg.label]}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={cfg.color}
              strokeWidth={2}
              fill="url(#chartGrad)"
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function SensorCard({
  label,
  value,
  unit,
  icon,
  isLive,
  subtext,
  badge,
  badgeColor,
}: {
  label: string;
  value: string;
  unit: string;
  icon: React.ReactNode;
  isLive: boolean;
  subtext?: string;
  badge?: string;
  badgeColor?: string;
}) {
  return (
    <div
      className="rounded-lg px-4 py-3 flex flex-col justify-between gap-1"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-widest font-medium" style={{ color: 'var(--text-muted)' }}>
          {label}
        </span>
        <span style={{ color: 'var(--text-muted)', opacity: 0.6 }}>{icon}</span>
      </div>

      <div className="my-0.5">
        <span className="font-mono-data text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {value}
        </span>
        {unit && <span className="ml-1 text-xs" style={{ color: 'var(--text-muted)' }}>{unit}</span>}
      </div>

      <div className="flex items-center justify-between text-[9px] pt-1 border-t border-slate-800/60">
        <span style={{ color: 'var(--text-muted)' }}>{subtext || (isLive ? 'Live Sensor' : 'Offline')}</span>
        {badge && (
          <span className="font-bold px-1.5 py-0.5 rounded text-[8px]" style={{ background: `${badgeColor}22`, color: badgeColor, border: `1px solid ${badgeColor}44` }}>
            {badge}
          </span>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ running, online, hasData }: { running: boolean; online: boolean; hasData: boolean }) {
  if (!hasData) {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-slate-800 border border-slate-700 text-slate-400">
        <div className="w-1.5 h-1.5 rounded-full bg-slate-500" />
        No Hardware Signal
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
      style={
        online
          ? { background: 'rgba(34,208,110,0.1)', border: '1px solid rgba(34,208,110,0.25)', color: 'var(--status-online)' }
          : { background: 'rgba(51,79,107,0.15)', border: '1px solid rgba(51,79,107,0.3)', color: 'var(--status-offline)' }
      }
    >
      <div className={`w-1.5 h-1.5 rounded-full ${online && running ? 'pulse-dot' : ''}`}
        style={{ background: online ? 'var(--status-online)' : 'var(--status-offline)' }}
      />
      {online ? (running ? 'Online (Motor Running)' : 'Online (Motor Idle)') : 'Offline'}
    </div>
  );
}

function IconGauge() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a10 10 0 0 1 7.38 16.75"/><path d="M12 2a10 10 0 0 0-7.38 16.75"/><line x1="12" y1="12" x2="15.5" y2="8.5"/><circle cx="12" cy="12" r="1"/></svg>;
}
function IconThermo() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>;
}
function IconDroplet() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>;
}
function IconZap() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>;
}
function IconWave() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 12h2.5c1 0 1.5-1 2-2s1-2 2-2 1.5 1 2 2 1 2 2 2 1.5-1 2-2 1-2 2-2 1.5 1 2 2 1 2 2 2"/></svg>;
}
function IconSliders() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/></svg>;
}
