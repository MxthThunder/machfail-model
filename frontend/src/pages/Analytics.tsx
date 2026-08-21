import { useState, useEffect, useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { fetchMotorHistory, type MotorTelemetryData } from '../services/api';

type MetricKey = 'rpm' | 'temperature' | 'current' | 'vibration';

const METRICS: { key: MetricKey; label: string; unit: string; color: string }[] = [
  { key: 'rpm',         label: 'Rotational Speed', unit: 'RPM', color: '#2b7fff' },
  { key: 'temperature', label: 'Temperature',      unit: '°C',  color: '#f59e0b' },
  { key: 'current',     label: 'Current Draw',     unit: 'A',   color: '#a78bfa' },
  { key: 'vibration',   label: 'Vibration',        unit: 'g',   color: '#22d06e' },
];

export default function Analytics() {
  const [history, setHistory] = useState<MotorTelemetryData[]>([]);
  const [activeMetric, setActiveMetric] = useState<MetricKey>('rpm');
  const [limit, setLimit] = useState<number>(50);

  useEffect(() => {
    let isMounted = true;

    async function loadHistory() {
      const data = await fetchMotorHistory('M001', limit);
      if (isMounted && data && data.records) {
        // Reverse so it displays chronologically from left to right
        setHistory([...data.records].reverse());
      }
    }

    loadHistory();
    const interval = setInterval(loadHistory, 4000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [limit]);

  // Compute real historical statistics from database records
  const stats = useMemo(() => {
    if (history.length === 0) {
      return [
        { label: 'Avg RPM',         value: '---', unit: 'RPM', color: '#2b7fff' },
        { label: 'Max Temperature', value: '---', unit: '°C',  color: '#f59e0b' },
        { label: 'Avg Current',     value: '---', unit: 'A',   color: '#a78bfa' },
        { label: 'Max Vibration',   value: '---', unit: 'g',   color: '#22d06e' },
        { label: 'Total DB Records',value: '0',   unit: 'pts', color: '#22d3ee' },
      ];
    }

    const avgRpm = history.reduce((acc, r) => acc + (r.rpm || 0), 0) / history.length;
    const maxTemp = Math.max(...history.map((r) => r.temperature || 0));
    const avgCurr = history.reduce((acc, r) => acc + (r.current || 0), 0) / history.length;
    const maxVib = Math.max(...history.map((r) => r.vibration || 0));

    return [
      { label: 'Avg RPM',         value: avgRpm.toFixed(1),   unit: 'RPM', color: '#2b7fff' },
      { label: 'Max Temperature', value: maxTemp.toFixed(1),  unit: '°C',  color: '#f59e0b' },
      { label: 'Avg Current',     value: avgCurr.toFixed(2),  unit: 'A',   color: '#a78bfa' },
      { label: 'Max Vibration',   value: maxVib.toFixed(3),   unit: 'g',   color: '#22d06e' },
      { label: 'Total DB Records',value: `${history.length}`, unit: 'pts', color: '#22d3ee' },
    ];
  }, [history]);

  const activeCfg = METRICS.find((m) => m.key === activeMetric)!;
  const chartData = history.map((record, index) => ({
    i: index + 1,
    time: record.timestamp ? new Date(record.timestamp).toLocaleTimeString() : `#${index + 1}`,
    value: record[activeMetric] !== undefined ? Number(record[activeMetric]) : 0,
  }));

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Real-Time Historical Telemetry (MOTOR-01)
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Queries persistent timestamped records directly from SQLite database (Zero fake generators).
          </p>
        </div>

        {/* Limit selector */}
        <div className="flex gap-1 p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          {[20, 50, 100].map((count) => (
            <button
              key={count}
              onClick={() => setLimit(count)}
              className={`px-3 py-1 rounded font-semibold transition ${
                limit === count ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Last {count}
            </button>
          ))}
        </div>
      </div>

      {/* Real Statistics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3.5">
        {stats.map(({ label, value, unit, color }) => (
          <div
            key={label}
            className="rounded-xl px-4 py-3 bg-slate-900/90 border border-slate-800 flex flex-col justify-between"
          >
            <div className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">{label}</div>
            <div className="my-1">
              <span className="font-mono text-2xl font-bold text-white">{value}</span>
              {unit && <span className="ml-1 text-xs text-slate-400">{unit}</span>}
            </div>
            <div className="text-[9px] text-slate-500">From SQLite DB</div>
          </div>
        ))}
      </div>

      {/* Historical Trend Chart */}
      <div className="rounded-2xl p-5 bg-slate-900/90 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white">Historical Metric:</span>
            <div className="flex gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
              {METRICS.map((m) => (
                <button
                  key={m.key}
                  onClick={() => setActiveMetric(m.key)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold transition ${
                    activeMetric === m.key
                      ? 'bg-slate-800 text-white shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                  style={activeMetric === m.key ? { color: m.color } : {}}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          <span className="text-xs font-mono text-slate-400">
            {history.length > 0 ? `Displaying ${history.length} physical records` : 'No database records yet'}
          </span>
        </div>

        {history.length === 0 ? (
          <div className="py-20 text-center text-xs text-slate-400 border border-dashed border-slate-800 rounded-xl">
            <div className="text-2xl mb-2">📡</div>
            <div className="font-semibold text-slate-300">Awaiting Telemetry from ESP32 Hardware</div>
            <p className="text-slate-500 mt-1">
              Once your ESP32 begins sending HTTP POST requests to <code>/api/motor/data</code>, historical time-series graphs will render here automatically.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="histGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={activeCfg.color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={activeCfg.color} stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(29,51,84,0.6)" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
                itemStyle={{ color: activeCfg.color, fontFamily: 'JetBrains Mono', fontSize: 12 }}
                formatter={(v) => [`${v} ${activeCfg.unit}`, activeCfg.label]}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke={activeCfg.color}
                strokeWidth={2}
                fill="url(#histGrad)"
                dot={false}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
