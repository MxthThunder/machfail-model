import { useState, useEffect } from 'react';
import Overview from './pages/Overview';
import MachineDetail from './pages/MachineDetail';
import MotorControl from './pages/MotorControl';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';
import AIPrediction from './pages/AIPrediction';
import SystemStatus from './pages/SystemStatus';

export type Page =
  | 'overview'
  | 'machine-detail'
  | 'motor-control'
  | 'analytics'
  | 'alerts'
  | 'ai-prediction'
  | 'system-status';

const NAV_ITEMS: { page: Page; label: string; icon: React.ReactNode }[] = [
  { page: 'overview', label: 'Overview', icon: <IconGrid /> },
  { page: 'machine-detail', label: 'Live Monitoring', icon: <IconActivity /> },
  { page: 'motor-control', label: 'Motor Control', icon: <IconSliders /> },
  { page: 'analytics', label: 'Analytics', icon: <IconBarChart /> },
  { page: 'alerts', label: 'Alerts', icon: <IconBell /> },
  { page: 'ai-prediction', label: 'AI Prediction', icon: <IconBrain /> },
];

export default function App() {
  const [activePage, setActivePage] = useState<Page>('overview');
  const [motorRunning, setMotorRunning] = useState(true);
  const [commandedSpeed, setCommandedSpeed] = useState(65);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [notifCount] = useState(2);

  useEffect(() => {
    if (!motorRunning) return;
    const id = setInterval(() => setLastUpdate(new Date()), 4000);
    return () => clearInterval(id);
  }, [motorRunning]);

  const pageTitle: Record<Page, string> = {
    overview: 'Machine Fleet Overview',
    'machine-detail': 'MOTOR-01 — Conveyor Motor',
    'motor-control': 'Motor Control Panel',
    analytics: 'Historical Analytics',
    alerts: 'Alert Management',
    'ai-prediction': 'AI Predictive Maintenance',
    'system-status': 'System Status',
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      {/* Sidebar */}
      <aside
        className="flex flex-col shrink-0 border-r"
        style={{
          width: 232,
          background: 'var(--bg-card)',
          borderColor: 'var(--border-dim)',
        }}
      >
        {/* Logo */}
        <div className="px-5 pt-6 pb-5 border-b" style={{ borderColor: 'var(--border-dim)' }}>
          <div className="flex items-center gap-2.5">
            <div
              className="flex items-center justify-center rounded"
              style={{
                width: 32,
                height: 32,
                background: 'var(--accent-blue)',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div className="font-bold text-sm tracking-widest" style={{ color: 'var(--text-primary)', letterSpacing: '0.12em' }}>
                INDUSTRIA
              </div>
              <div className="text-[10px] tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Machine Intelligence
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5 overflow-y-auto">
          <div className="px-2 pb-2 text-[10px] font-semibold tracking-widest uppercase" style={{ color: 'var(--text-muted)' }}>
            Navigation
          </div>
          {/* Overview first item not in NAV_ITEMS */}
          <NavItem
            label="Overview"
            icon={<IconGrid />}
            active={activePage === 'overview'}
            onClick={() => setActivePage('overview')}
          />
          {NAV_ITEMS.filter(n => n.page !== 'overview').map(({ page, label, icon }) => (
            <NavItem
              key={page}
              label={label}
              icon={icon}
              active={activePage === page}
              onClick={() => setActivePage(page)}
            />
          ))}

          {/* Spacer */}
          <div className="flex-1" />

          {/* Bottom section */}
          <div className="pt-3 border-t mt-2" style={{ borderColor: 'var(--border-dim)' }}>
            <NavItem
              label="System Status"
              icon={<IconServer />}
              active={activePage === 'system-status'}
              onClick={() => setActivePage('system-status')}
            />
          </div>
        </nav>

        {/* ESP32 status */}
        <div className="px-4 py-3 border-t" style={{ borderColor: 'var(--border-dim)' }}>
          <div className="flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full pulse-dot"
              style={{ background: 'var(--status-online)' }}
            />
            <div>
              <div className="text-[10px] font-medium" style={{ color: 'var(--text-muted)' }}>
                ESP32 Network
              </div>
              <div className="text-[11px] font-semibold" style={{ color: 'var(--status-online)' }}>
                Connected
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Header */}
        <header
          className="shrink-0 flex items-center justify-between px-6 border-b"
          style={{
            height: 60,
            background: 'var(--bg-card)',
            borderColor: 'var(--border-dim)',
          }}
        >
          <div>
            <h1 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
              {pageTitle[activePage]}
            </h1>
            {activePage === 'machine-detail' && (
              <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
                Industrial Conveyor Drive System · Unit #A14
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Connection status */}
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium"
              style={{
                background: 'rgba(34,208,110,0.08)',
                border: '1px solid rgba(34,208,110,0.18)',
                color: 'var(--status-online)',
              }}
            >
              <div className="w-1.5 h-1.5 rounded-full pulse-dot" style={{ background: 'var(--status-online)' }} />
              System Online
            </div>

            {/* Last update */}
            <div className="text-[11px] font-mono-data" style={{ color: 'var(--text-muted)' }}>
              {motorRunning ? (
                <>Updated {lastUpdate.toLocaleTimeString()}</>
              ) : (
                <span style={{ color: 'var(--status-warning)' }}>Motor offline</span>
              )}
            </div>

            {/* Notification bell */}
            <button
              className="relative flex items-center justify-center rounded transition-fast hover:opacity-80"
              style={{ width: 32, height: 32, background: 'var(--bg-card2)', border: '1px solid var(--border-mid)' }}
            >
              <IconBell size={15} />
              {notifCount > 0 && (
                <span
                  className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[9px] font-bold flex items-center justify-center"
                  style={{ background: 'var(--status-critical)', color: 'white' }}
                >
                  {notifCount}
                </span>
              )}
            </button>

            {/* User */}
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded"
              style={{ background: 'var(--bg-card2)', border: '1px solid var(--border-mid)' }}
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold"
                style={{ background: 'var(--accent-blue)', color: 'white' }}
              >
                E
              </div>
              <span className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>Engineer</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {activePage === 'overview' && (
            <Overview
              motorRunning={motorRunning}
              onViewMachine={() => setActivePage('machine-detail')}
            />
          )}
          {activePage === 'machine-detail' && (
            <MachineDetail
              motorRunning={motorRunning}
              onBack={() => setActivePage('overview')}
            />
          )}
          {activePage === 'motor-control' && (
            <MotorControl
              motorRunning={motorRunning}
              setMotorRunning={setMotorRunning}
              commandedSpeed={commandedSpeed}
              setCommandedSpeed={setCommandedSpeed}
            />
          )}
          {activePage === 'analytics' && <Analytics />}
          {activePage === 'alerts' && <Alerts />}
          {activePage === 'ai-prediction' && <AIPrediction motorRunning={motorRunning} />}
          {activePage === 'system-status' && <SystemStatus motorRunning={motorRunning} />}
        </main>
      </div>
    </div>
  );
}

function NavItem({
  label,
  icon,
  active,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2 rounded text-left transition-fast text-xs font-medium"
      style={{
        background: active ? 'rgba(43,127,255,0.12)' : 'transparent',
        color: active ? 'var(--accent-blue)' : 'var(--text-muted)',
        border: active ? '1px solid rgba(43,127,255,0.2)' : '1px solid transparent',
      }}
    >
      <span className="shrink-0 opacity-80">{icon}</span>
      {label}
    </button>
  );
}

function IconGrid() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}
function IconActivity() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}
function IconSliders() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="4" y1="21" x2="4" y2="14" /><line x1="4" y1="10" x2="4" y2="3" />
      <line x1="12" y1="21" x2="12" y2="12" /><line x1="12" y1="8" x2="12" y2="3" />
      <line x1="20" y1="21" x2="20" y2="16" /><line x1="20" y1="12" x2="20" y2="3" />
      <line x1="1" y1="14" x2="7" y2="14" /><line x1="9" y1="8" x2="15" y2="8" />
      <line x1="17" y1="16" x2="23" y2="16" />
    </svg>
  );
}
function IconBarChart() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" /><line x1="2" y1="20" x2="22" y2="20" />
    </svg>
  );
}
function IconBell({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}
function IconBrain() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
    </svg>
  );
}
function IconPresentation() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h20" /><path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3" />
      <path d="m7 21 5-5 5 5" />
    </svg>
  );
}
function IconServer() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
      <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
      <line x1="6" y1="6" x2="6.01" y2="6" /><line x1="6" y1="18" x2="6.01" y2="18" />
    </svg>
  );
}
