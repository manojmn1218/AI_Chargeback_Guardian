import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  Shield,
  Zap,
  Search,
  Settings,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, shortLabel: 'Home' },
  { to: '/analytics', label: 'Analytics', icon: BarChart3, shortLabel: 'Stats' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside
      className="fixed left-0 top-0 h-screen w-[72px] flex flex-col items-center py-5 transition-all duration-500"
      style={{
        zIndex: 30,
        background: 'rgba(8, 10, 28, 0.6)',
        backdropFilter: 'blur(40px) saturate(2)',
        WebkitBackdropFilter: 'blur(40px) saturate(2)',
        borderRight: '1px solid rgba(99, 102, 241, 0.08)',
      }}
    >
      {/* Brand mark */}
      <div className="mb-8">
        <div
          className="w-11 h-11 rounded-2xl flex items-center justify-center relative group cursor-pointer transition-all duration-500 hover:scale-105"
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4)',
            boxShadow: '0 0 24px rgba(99, 102, 241, 0.35), inset 0 1px 0 rgba(255,255,255,0.15)',
          }}
        >
          <Shield className="w-5 h-5 text-white" strokeWidth={2.5} />
          {/* Orbiting ring */}
          <div
            className="absolute inset-[-3px] rounded-2xl animate-spin"
            style={{
              background: 'conic-gradient(from 0deg, transparent 70%, rgba(99, 102, 241, 0.3) 100%)',
              animationDuration: '4s',
              mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
              WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
              WebkitMaskComposite: 'xor',
              maskComposite: 'exclude',
              padding: '1.5px',
            }}
          />
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 flex flex-col items-center gap-2">
        {navItems.map(({ to, label, icon: Icon, shortLabel }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className="group relative"
          >
            {({ isActive }) => (
              <>
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-300"
                  style={{
                    background: isActive
                      ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.2))'
                      : 'transparent',
                    border: isActive ? '1px solid rgba(99, 102, 241, 0.25)' : '1px solid transparent',
                    boxShadow: isActive ? '0 0 20px rgba(99, 102, 241, 0.15), inset 0 1px 0 rgba(255,255,255,0.05)' : 'none',
                  }}
                >
                  <Icon
                    className="w-[20px] h-[20px] transition-all duration-300"
                    style={{
                      color: isActive ? '#a5b4fc' : 'rgba(148, 163, 184, 0.6)',
                      filter: isActive ? 'drop-shadow(0 0 6px rgba(99, 102, 241, 0.5))' : 'none',
                    }}
                    strokeWidth={isActive ? 2.2 : 1.8}
                  />
                </div>

                {/* Active dot */}
                {isActive && (
                  <div
                    className="absolute -right-[5px] top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-l-full"
                    style={{
                      background: 'linear-gradient(180deg, #6366f1, #06b6d4)',
                      boxShadow: '0 0 8px rgba(99, 102, 241, 0.6)',
                    }}
                  />
                )}

                {/* Tooltip */}
                <div
                  className="absolute left-full ml-3 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap pointer-events-none"
                  style={{
                    background: 'rgba(15, 20, 50, 0.95)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                    color: '#f0f2f8',
                    fontSize: '12px',
                    fontWeight: 600,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
                    backdropFilter: 'blur(12px)',
                  }}
                >
                  {label}
                  <ChevronRight className="inline w-3 h-3 ml-1 opacity-40" />
                </div>

                {/* Label under icon */}
                <div
                  className="text-[9px] font-bold uppercase tracking-wider text-center mt-0.5 transition-colors duration-300"
                  style={{
                    color: isActive ? 'rgba(165, 180, 252, 0.8)' : 'rgba(100, 116, 139, 0.5)',
                  }}
                >
                  {shortLabel}
                </div>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom section */}
      <div className="flex flex-col items-center gap-3">
        {/* Settings icon */}
        <button
          className="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 group"
          style={{
            background: 'transparent',
            border: '1px solid transparent',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.08)';
            e.currentTarget.style.border = '1px solid rgba(99, 102, 241, 0.12)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.border = '1px solid transparent';
          }}
        >
          <Settings className="w-[18px] h-[18px] transition-all duration-500 group-hover:rotate-90" style={{ color: 'rgba(100, 116, 139, 0.5)' }} />
        </button>

        {/* Status dot */}
        <div className="relative">
          <div className="w-2.5 h-2.5 rounded-full animate-pulse" style={{ backgroundColor: '#22c55e', boxShadow: '0 0 8px rgba(34, 197, 94, 0.5)' }} />
        </div>
      </div>
    </aside>
  );
}
