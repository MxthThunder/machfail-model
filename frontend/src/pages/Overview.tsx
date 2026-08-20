const MACHINES = [
  {
    id: 'MOTOR-01',
    type: 'Conveyor Motor',
    img: 'https://images.unsplash.com/photo-1692719094491-2746e82a8595?w=400&h=240&fit=crop&auto=format',
    online: true,
    health: 92,
    rpm: 1450,
    unit: '#A14',
  },
  {
    id: 'MOTOR-02',
    type: 'Pump Motor',
    img: 'https://images.unsplash.com/photo-1649038780045-235e4b6e40b4?w=400&h=240&fit=crop&auto=format',
    online: false,
    health: null,
    rpm: null,
    unit: '#B02',
  },
  {
    id: 'MOTOR-03',
    type: 'Compressor Motor',
    img: 'https://images.unsplash.com/photo-1720036236855-9a1a2e4d3f26?w=400&h=240&fit=crop&auto=format',
    online: false,
    health: null,
    rpm: null,
    unit: '#C07',
  },
  {
    id: 'MOTOR-04',
    type: 'Cooling Motor',
    img: 'https://images.unsplash.com/photo-1555941911-2c0c77a44ea4?w=400&h=240&fit=crop&auto=format',
    online: false,
    health: null,
    rpm: null,
    unit: '#D11',
  },
  {
    id: 'MOTOR-05',
    type: 'Conveyor Motor',
    img: 'https://images.unsplash.com/photo-1655874837055-7adc909ae602?w=400&h=240&fit=crop&auto=format',
    online: false,
    health: null,
    rpm: null,
    unit: '#A22',
  },
  {
    id: 'MOTOR-06',
    type: 'Hydraulic Motor',
    img: 'https://images.unsplash.com/photo-1565377167263-d29b5ac85479?w=400&h=240&fit=crop&auto=format',
    online: false,
    health: null,
    rpm: null,
    unit: '#F03',
  },
];

const SUMMARY = [
  { label: 'Total Machines', value: 6, color: 'var(--accent-blue)' },
  { label: 'Online', value: 1, color: 'var(--status-online)' },
  { label: 'Offline', value: 5, color: 'var(--status-offline)' },
  { label: 'Active Alerts', value: 0, color: 'var(--text-muted)' },
];

export default function Overview({
  motorRunning,
  onViewMachine,
}: {
  motorRunning: boolean;
  onViewMachine: () => void;
}) {
  return (
    <div className="p-6 space-y-6">
      {/* Summary row */}
      <div className="grid grid-cols-4 gap-4">
        {SUMMARY.map(({ label, value, color }) => (
          <div
            key={label}
            className="rounded-lg px-5 py-4 flex flex-col gap-1"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-dim)' }}
          >
            <span className="text-[11px] uppercase tracking-widest font-medium" style={{ color: 'var(--text-muted)' }}>
              {label}
            </span>
            <span className="text-3xl font-bold font-mono-data" style={{ color }}>
              {value}
            </span>
          </div>
        ))}
      </div>

      {/* Section label */}
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
          Machine Fleet
        </h2>
        <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          6 units registered
        </span>
      </div>

      {/* Machine grid */}
      <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {MACHINES.map((m) => {
          const isM1 = m.id === 'MOTOR-01';
          const isOnline = isM1 ? motorRunning : false;
          return (
            <MachineCard
              key={m.id}
              machine={m}
              isOnline={isOnline}
              onView={isM1 ? onViewMachine : undefined}
            />
          );
        })}
      </div>
    </div>
  );
}

function MachineCard({
  machine,
  isOnline,
  onView,
}: {
  machine: typeof MACHINES[number];
  isOnline: boolean;
  onView?: () => void;
}) {
  return (
    <div
      className="rounded-lg overflow-hidden flex flex-col"
      style={{
        background: 'var(--bg-card)',
        border: isOnline ? '1px solid rgba(34,208,110,0.25)' : '1px solid var(--border-dim)',
        boxShadow: isOnline ? '0 0 20px rgba(34,208,110,0.06)' : 'none',
      }}
    >
      {/* Image */}
      <div className="relative overflow-hidden" style={{ height: 160, background: '#0a1520' }}>
        <img
          src={machine.img}
          alt={`${machine.id} - ${machine.type}`}
          className="w-full h-full object-cover"
          style={{ opacity: isOnline ? 0.9 : 0.35, filter: isOnline ? 'none' : 'grayscale(60%)' }}
        />
        {/* Status badge */}
        <div className="absolute top-3 right-3">
          <StatusBadge online={isOnline} />
        </div>
        {/* Machine ID overlay */}
        <div
          className="absolute bottom-0 left-0 right-0 px-3 py-2"
          style={{ background: 'linear-gradient(to top, rgba(6,15,28,0.9), transparent)' }}
        >
          <span className="font-mono-data text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>
            {machine.id}
          </span>
          <span className="ml-2 text-[10px]" style={{ color: 'var(--text-muted)' }}>
            {machine.unit}
          </span>
        </div>
      </div>

      {/* Card body */}
      <div className="p-4 flex flex-col gap-3 flex-1">
        <div>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            {machine.id}
          </div>
          <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {machine.type}
          </div>
        </div>

        {isOnline && machine.health !== null ? (
          <div className="space-y-2">
            {/* Health bar */}
            <div className="flex items-center justify-between text-[11px]">
              <span style={{ color: 'var(--text-muted)' }}>Health</span>
              <span className="font-mono-data font-semibold" style={{ color: 'var(--status-online)' }}>
                {machine.health}%
              </span>
            </div>
            <div className="h-1.5 rounded-full" style={{ background: 'var(--border-mid)' }}>
              <div
                className="h-full rounded-full"
                style={{ width: `${machine.health}%`, background: 'var(--status-online)' }}
              />
            </div>

            {/* RPM */}
            <div className="flex items-center justify-between text-[11px] pt-1">
              <span style={{ color: 'var(--text-muted)' }}>Current RPM</span>
              <span className="font-mono-data font-semibold" style={{ color: 'var(--accent-blue)' }}>
                {machine.rpm?.toLocaleString()} RPM
              </span>
            </div>
          </div>
        ) : (
          <div
            className="flex items-center justify-center rounded py-3 text-xs"
            style={{ background: 'var(--bg-card2)', color: 'var(--text-muted)' }}
          >
            No data available — machine offline
          </div>
        )}

        {/* Button */}
        <button
          onClick={onView}
          className="mt-auto w-full py-2 rounded text-xs font-semibold transition-fast"
          style={
            isOnline
              ? {
                  background: 'rgba(43,127,255,0.12)',
                  border: '1px solid rgba(43,127,255,0.3)',
                  color: 'var(--accent-blue)',
                }
              : {
                  background: 'var(--bg-card2)',
                  border: '1px solid var(--border-dim)',
                  color: 'var(--text-muted)',
                  cursor: onView ? 'pointer' : 'default',
                }
          }
        >
          {isOnline ? 'View Machine →' : 'View Machine'}
        </button>
      </div>
    </div>
  );
}

function StatusBadge({ online }: { online: boolean }) {
  return (
    <div
      className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
      style={
        online
          ? { background: 'rgba(34,208,110,0.15)', border: '1px solid rgba(34,208,110,0.3)', color: 'var(--status-online)' }
          : { background: 'rgba(51,79,107,0.25)', border: '1px solid rgba(51,79,107,0.4)', color: 'var(--status-offline)' }
      }
    >
      <div
        className="w-1.5 h-1.5 rounded-full"
        style={{ background: online ? 'var(--status-online)' : 'var(--status-offline)' }}
      />
      {online ? 'Online' : 'Offline'}
    </div>
  );
}
