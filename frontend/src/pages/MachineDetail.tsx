import { useState, useEffect, useRef } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

type Metric = 'rpm' | 'temperature' | 'current' | 'voltage' | 'vibration';
type TimeRange = '1m' | '5m' | '1h' | '24h';

const METRIC_CONFIG: Record<Metric, { label: string; unit: string; base: number; variance: number; color: string }> = {
  rpm:         { label: 'RPM',         unit: 'RPM',  base: 1450, variance: 60,   color: '#2b7fff' },
  temperature: { label: 'Temperature', unit: '°C',   base: 42.5, variance: 3,    color: '#f59e0b' },
  current:     { label: 'Current',     unit: 'A',    base: 1.2,  variance: 0.25, color: '#a78bfa' },
  voltage:     { label: 'Voltage',     unit: 'V',    base: 9.1,  variance: 0.4,  color: '#22d3ee' },
  vibration:   { label: 'Vibration',   unit: 'g',    base: 0.05, variance: 0.02, color: '#22d06e' },
};

const TIME_RANGES: { key: TimeRange; label: string; points: number }[] = [
  { key: '1m',  label: '1 Min',  points: 60  },
  { key: '5m',  label: '5 Min',  points: 60  },
  { key: '1h',  label: '1 Hour', points: 60  },
  { key: '24h', label: '24 Hours', points: 72 },
];

function generateSeries(points: number, base: number, variance: number) {
  let v = base;
  return Array.from({ length: points }, (_, i) => {
    v += (Math.random() - 0.5) * variance * 0.4;
    v = Math.max(base - variance, Math.min(base + variance, v));
    return { i, value: parseFloat(v.toFixed(2)) };
  });
}

const LAST_RECORDED = {
  rpm: 1450, temp: 42.5, humidity: 58, current: 1.2, voltage: 9.1, vibration: 'NORMAL',
};

export default function MachineDetail({
  motorRunning,
  onBack,
}: {
  motorRunning: boolean;
  onBack: () => void;
}) {
  const [metric, setMetric] = useState<Metric>('rpm');
  const [timeRange, setTimeRange] = useState<TimeRange>('5m');
  const [chartData, setChartData] = useState(() => {
    const cfg = METRIC_CONFIG.rpm;
    return generateSeries(60, cfg.base, cfg.variance);
  });
  const tickRef = useRef(0);

  // Regenerate when metric changes
  useEffect(() => {
    const cfg = METRIC_CONFIG[metric];
    const t = TIME_RANGES.find(r => r.key === timeRange)!;
    setChartData(generateSeries(t.points, cfg.base, cfg.variance));
  }, [metric, timeRange]);

  // Live tick every second when running
  useEffect(() => {
    if (!motorRunning) return;
    const cfg = METRIC_CONFIG[metric];
    const id = setInterval(() => {
      tickRef.current++;
      setChartData(prev => {
        const last = prev[prev.length - 1].value;
        const next = parseFloat(
          Math.max(cfg.base - cfg.variance, Math.min(cfg.base + cfg.variance,
            last + (Math.random() - 0.5) * cfg.variance * 0.35
          )).toFixed(2)
        );
        const t = TIME_RANGES.find(r => r.key === timeRange)!;
        return [...prev.slice(-(t.points - 1)), { i: tickRef.current, value: next }];
      });
    }, 1000);
    return () => clearInterval(id);
  }, [motorRunning, metric, timeRange]);

  const cfg = METRIC_CONFIG[metric];
  const latest = chartData[chartData.length - 1]?.value ?? 0;

  const sensorCards = [
    { label: 'RPM', value: motorRunning ? '1,450' : null, unit: 'RPM', last: '1,450', icon: <IconGauge />, ok: true },
    { label: 'Temperature', value: motorRunning ? '42.5' : null, unit: '°C', last: '42.5', icon: <IconThermo />, ok: true },
    { label: 'Humidity', value: motorRunning ? '58' : null, unit: '%', last: '58', icon: <IconDroplet />, ok: true },
    { label: 'Current', value: motorRunning ? '1.2' : null, unit: 'A', last: '1.2', icon: <IconZap />, ok: true },
    { label: 'Voltage', value: motorRunning ? '9.1' : null, unit: 'V', last: '9.1', icon: <IconBattery />, ok: true },
    { label: 'Vibration', value: motorRunning ? 'NORMAL' : null, unit: '', last: 'NORMAL', icon: <IconWave />, ok: true, isText: true },
  ];

  return (
    <div className="p-6 space-y-5">
      {/* Back + title */}
      <div className="flex items-start justify-between">
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
            <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>MOTOR-01</h2>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Conveyor Motor</span>
            <StatusBadge running={motorRunning} />
          </div>
        </div>
        <div className="text-right">
          <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Serial</div>
          <div className="font-mono-data text-xs" style={{ color: 'var(--text-primary)' }}>ESP-A14-CM-001</div>
        </div>
      </div>

      {/* Offline notice */}
      {!motorRunning && (
        <div
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm"
          style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)', color: 'var(--status-warning)' }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Motor is currently stopped. Showing last recorded sensor values.
        </div>
      )}

      {/* Sensor cards */}
      <div className="grid grid-cols-3 gap-3 md:grid-cols-6">
        {sensorCards.map((sc) => (
          <div
            key={sc.label}
            className="rounded-lg px-4 py-3 flex flex-col gap-1"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-widest font-medium" style={{ color: 'var(--text-muted)' }}>
                {sc.label}
              </span>
              <span style={{ color: 'var(--text-muted)', opacity: 0.6 }}>{sc.icon}</span>
            </div>
            {sc.value !== null ? (
              <div>
                <span className="font-mono-data text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {sc.value}
                </span>
                {sc.unit && (
                  <span className="ml-1 text-xs" style={{ color: 'var(--text-muted)' }}>{sc.unit}</span>
                )}
              </div>
            ) : (
              <div>
                <span className="font-mono-data text-xl font-bold" style={{ color: 'var(--text-muted)' }}>
                  {sc.last}
                </span>
                {sc.unit && (
                  <span className="ml-1 text-xs" style={{ color: 'var(--text-muted)' }}>{sc.unit}</span>
                )}
                <div className="text-[9px] mt-0.5 uppercase tracking-wider" style={{ color: 'var(--text-muted)', opacity: 0.6 }}>
                  Last recorded
                </div>
              </div>
            )}
            {/* Status dot */}
            <div className="flex items-center gap-1 mt-0.5">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: sc.value !== null ? 'var(--status-online)' : 'var(--status-offline)' }}
              />
              <span className="text-[9px] uppercase tracking-wider" style={{ color: sc.value !== null ? 'var(--status-online)' : 'var(--text-muted)' }}>
                {sc.value !== null ? 'Live' : 'Stale'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Live chart */}
      <div
        className="rounded-lg p-5"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        {/* Chart header */}
        <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full pulse-dot" style={{ background: cfg.color }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Live: {cfg.label}
            </span>
            <span className="font-mono-data text-xs px-2 py-0.5 rounded" style={{ background: 'var(--bg-card2)', color: cfg.color }}>
              {latest} {cfg.unit}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Metric selector */}
            <div className="flex gap-1 p-1 rounded" style={{ background: 'var(--bg-card2)' }}>
              {(Object.keys(METRIC_CONFIG) as Metric[]).map(m => (
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
              {TIME_RANGES.map(t => (
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
          <AreaChart data={chartData} margin={{ top: 5, right: 8, left: -10, bottom: 0 }}>
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

function StatusBadge({ running }: { running: boolean }) {
  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
      style={
        running
          ? { background: 'rgba(34,208,110,0.1)', border: '1px solid rgba(34,208,110,0.25)', color: 'var(--status-online)' }
          : { background: 'rgba(51,79,107,0.15)', border: '1px solid rgba(51,79,107,0.3)', color: 'var(--status-offline)' }
      }
    >
      <div className={`w-1.5 h-1.5 rounded-full ${running ? 'pulse-dot' : ''}`}
        style={{ background: running ? 'var(--status-online)' : 'var(--status-offline)' }}
      />
      {running ? 'Online' : 'Offline'}
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
function IconBattery() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="1" y="6" width="18" height="12" rx="2"/><line x1="23" y1="13" x2="23" y2="11"/></svg>;
}
function IconWave() {
  return <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 12h2.5c1 0 1.5-1 2-2s1-2 2-2 1.5 1 2 2 1 2 2 2 1.5-1 2-2 1-2 2-2 1.5 1 2 2 1 2 2 2"/></svg>;
}
