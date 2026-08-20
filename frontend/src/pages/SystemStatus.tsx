const COMPONENTS = [
  { label: 'ESP32 Microcontroller', sub: 'ESP32-WROOM-32', icon: '🔌', alwaysOnline: true },
  { label: 'Wi-Fi Network',         sub: 'SSID: FACTORY_IoT_5G', icon: '📶', alwaysOnline: true },
  { label: 'RPM Sensor',            sub: 'Hall Effect — GPIO 34', icon: '⚙️', alwaysOnline: true },
  { label: 'DHT22 Sensor',          sub: 'Temp + Humidity — GPIO 4', icon: '🌡️', alwaysOnline: true },
  { label: 'MPU6050',               sub: 'Accelerometer + Gyro — I²C', icon: '📐', alwaysOnline: true },
  { label: 'ACS712',                sub: 'Current Sensor — ADC1', icon: '⚡', alwaysOnline: true },
  { label: 'Motor Drive',           sub: 'PWM via MOSFET bridge', icon: '🔧', alwaysOnline: false },
];

const NETWORK_INFO = [
  { label: 'IP Address',      value: '192.168.1.142' },
  { label: 'Gateway',         value: '192.168.1.1' },
  { label: 'Signal Strength', value: '-58 dBm (Good)' },
  { label: 'MQTT Broker',     value: '192.168.1.10:1883' },
  { label: 'Uptime',          value: '14h 22m 05s' },
  { label: 'Firmware',        value: 'v1.4.2 (latest)' },
];

export default function SystemStatus({ motorRunning }: { motorRunning: boolean }) {
  return (
    <div className="p-6 w-full space-y-5">
      <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>System Health</h2>

      {/* Component status */}
      <div
        className="rounded-lg overflow-hidden"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="px-4 py-2.5 border-b text-[10px] uppercase tracking-widest font-semibold" style={{ color: 'var(--text-muted)', borderColor: 'var(--border-dim)' }}>
          Hardware Components
        </div>
        {COMPONENTS.map((c, i) => {
          const isOnline = c.alwaysOnline || motorRunning;
          return (
            <div
              key={c.label}
              className="flex items-center gap-4 px-4 py-3"
              style={{ borderTop: i > 0 ? '1px solid var(--border-dim)' : 'none' }}
            >
              <span className="text-base">{c.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>{c.label}</div>
                <div className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{c.sub}</div>
              </div>
              <ConnBadge online={isOnline} label={c.label === 'Motor Drive' ? (isOnline ? 'Running' : 'Stopped') : (isOnline ? 'Connected' : 'Offline')} />
            </div>
          );
        })}
      </div>

      {/* Network info */}
      <div
        className="rounded-lg overflow-hidden"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="px-4 py-2.5 border-b text-[10px] uppercase tracking-widest font-semibold" style={{ color: 'var(--text-muted)', borderColor: 'var(--border-dim)' }}>
          Network & Firmware
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x" style={{ borderColor: 'var(--border-dim)' }}>
          {NETWORK_INFO.map(({ label, value }) => (
            <div key={label} className="px-4 py-3 flex items-center justify-between" style={{ borderColor: 'var(--border-dim)' }}>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</span>
              <span className="font-mono-data text-xs font-medium" style={{ color: 'var(--text-primary)' }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* System diagnostics */}
      <div
        className="rounded-lg p-4 space-y-3"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
      >
        <div className="text-[10px] uppercase tracking-widest font-semibold" style={{ color: 'var(--text-muted)' }}>
          ESP32 Diagnostics
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { label: 'Free Heap',     value: '182 KB',  pct: 72 },
            { label: 'CPU Usage',     value: '18%',     pct: 18 },
            { label: 'Flash Used',    value: '1.1 MB',  pct: 55 },
          ].map(({ label, value, pct }) => (
            <div key={label}>
              <div className="flex items-center justify-between text-[11px] mb-1.5">
                <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                <span className="font-mono-data" style={{ color: 'var(--text-primary)' }}>{value}</span>
              </div>
              <div className="h-1.5 rounded-full" style={{ background: 'var(--border-mid)' }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${pct}%`,
                    background: pct > 80 ? 'var(--status-critical)' : pct > 60 ? 'var(--status-warning)' : 'var(--accent-blue)',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ConnBadge({ online, label }: { online: boolean; label: string }) {
  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-semibold"
      style={
        online
          ? { background: 'rgba(34,208,110,0.08)', border: '1px solid rgba(34,208,110,0.2)', color: 'var(--status-online)' }
          : { background: 'rgba(51,79,107,0.15)', border: '1px solid rgba(51,79,107,0.3)', color: 'var(--status-offline)' }
      }
    >
      <div
        className={`w-1.5 h-1.5 rounded-full ${online ? 'pulse-dot' : ''}`}
        style={{ background: online ? 'var(--status-online)' : 'var(--status-offline)' }}
      />
      {label}
    </div>
  );
}
