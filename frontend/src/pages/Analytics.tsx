import { useState, useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

type Range = 'hour' | 'today' | '7d' | '30d';

const RANGES: { key: Range; label: string; points: number }[] = [
  { key: 'hour', label: 'Last Hour', points: 60 },
  { key: 'today', label: 'Today', points: 96 },
  { key: '7d', label: '7 Days', points: 84 },
  { key: '30d', label: '30 Days', points: 90 },
];

function genSeries(points: number, base: number, variance: number) {
  let v = base;
  return Array.from({ length: points }, (_, i) => {
    v += (Math.random() - 0.5) * variance * 0.5;
    v = Math.max(base - variance, Math.min(base + variance, v));
    return { i, value: parseFloat(v.toFixed(2)) };
  });
}

const CHARTS = [
  { key: 'rpm',   label: 'RPM',         unit: 'RPM', base: 1450, variance: 80,  color: '#2b7fff' },
  { key: 'temp',  label: 'Temperature', unit: '°C',  base: 42,   variance: 5,   color: '#f59e0b' },
  { key: 'cur',   label: 'Current',     unit: 'A',   base: 1.2,  variance: 0.3, color: '#a78bfa' },
  { key: 'volt',  label: 'Voltage',     unit: 'V',   base: 9.1,  variance: 0.5, color: '#22d3ee' },
  { key: 'vib',   label: 'Vibration',   unit: 'g',   base: 0.05, variance: 0.03,color: '#22d06e' },
];

export default function Analytics({ motorRunning }: { motorRunning: boolean }) {
  const [range, setRange] = useState<Range>('today');

  const pts = RANGES.find(r => r.key === range)!.points;

  const datasets = useMemo(() => {
    return Object.fromEntries(CHARTS.map(c => [c.key, genSeries(pts, c.base, c.variance)]));
  }, [range]); // eslint-disable-line react-hooks/exhaustive-deps

  const stats = [
    { label: 'Avg RPM',       value: '1,447',  unit: 'RPM', color: '#2b7fff' },
    { label: 'Max Temperature', value: '46.2',  unit: '°C',  color: '#f59e0b' },
    { label: 'Avg Current',   value: '1.19',   unit: 'A',   color: '#a78bfa' },
    { label: 'Max Vibration', value: '0.072',  unit: 'g',   color: '#22d06e' },
    { label: 'Total Runtime', value: '142',    unit: 'hrs', color: '#22d3ee' },
  ];

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Historical Analytics — MOTOR-01</h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {motorRunning ? 'Live data collection active' : 'Motor offline — historical data only'}
          </p>
        </div>
        {/* Range selector */}
        <div className="flex gap-1 p-1 rounded" style={{ background: 'var(--bg-card)' }}>
          {RANGES.map(r => (
            <button
              key={r.key}
              onClick={() => setRange(r.key)}
              className="px-3 py-1.5 rounded text-xs font-medium transition-fast"
              style={
                range === r.key
                  ? { background: 'rgba(43,127,255,0.15)', color: 'var(--accent-blue)', border: '1px solid rgba(43,127,255,0.3)' }
                  : { color: 'var(--text-muted)', border: '1px solid transparent' }
              }
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-5 gap-3">
        {stats.map(s => (
          <div
            key={s.label}
            className="rounded-lg px-4 py-3"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
          >
            <div className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
            <div>
              <span className="font-mono-data text-xl font-bold" style={{ color: s.color }}>{s.value}</span>
              <span className="ml-1 text-[10px]" style={{ color: 'var(--text-muted)' }}>{s.unit}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts grid */}
      <div className="space-y-4">
        {CHARTS.map(c => (
          <MiniChart
            key={c.key}
            label={c.label}
            unit={c.unit}
            data={datasets[c.key] ?? []}
            color={c.color}
          />
        ))}
      </div>
    </div>
  );
}

function MiniChart({
  label, unit, data, color,
}: {
  label: string; unit: string; data: { i: number; value: number }[]; color: string;
}) {
  const vals = data.map(d => d.value);
  const min = Math.min(...vals).toFixed(2);
  const max = Math.max(...vals).toFixed(2);
  const avg = (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2);

  return (
    <div
      className="rounded-lg p-4"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: color }} />
          <span className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{label}</span>
        </div>
        <div className="flex gap-4 text-[11px] font-mono-data">
          <span style={{ color: 'var(--text-muted)' }}>Min <span style={{ color: 'var(--text-primary)' }}>{min}</span></span>
          <span style={{ color: 'var(--text-muted)' }}>Avg <span style={{ color }}>{avg}</span></span>
          <span style={{ color: 'var(--text-muted)' }}>Max <span style={{ color: 'var(--text-primary)' }}>{max}</span></span>
          <span style={{ color: 'var(--text-muted)' }}>{unit}</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id={`g-${label}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.2} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(29,51,84,0.5)" vertical={false} />
          <XAxis dataKey="i" hide />
          <YAxis domain={['auto', 'auto']} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-card2)', border: '1px solid var(--border-mid)', borderRadius: 6 }}
            labelStyle={{ display: 'none' }}
            itemStyle={{ color, fontFamily: 'JetBrains Mono', fontSize: 11 }}
            formatter={(v) => [`${v} ${unit}`, label]}
          />
          <Area type="monotone" dataKey="value" stroke={color} strokeWidth={1.5} fill={`url(#g-${label})`} dot={false} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
