import { Outlet, useLocation, NavLink, Link, useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { useAuth, DEMO_PERSONAS } from '../context/AuthContext';
import CyberBackground from '../components/CyberBackground';
import LiveCyberTicker from '../components/LiveCyberTicker';
import {
  Shield,
  LayoutDashboard,
  BarChart3,
  Volume2,
  VolumeX,
  Lock,
  UserCheck,
  LogOut,
  ChevronDown,
  Sparkles,
  KeyRound,
  User,
} from 'lucide-react';
import { cyberSound } from '../utils/cyberSound';

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, loginWithPersona, logout } = useAuth();

  const [audioEnabled, setAudioEnabled] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const dropdownRef = useRef(null);

  const toggleSound = () => {
    const nextState = cyberSound.toggle();
    setAudioEnabled(nextState);
    if (nextState) cyberSound.playSuccess();
  };

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div
      className="min-h-screen relative font-sans text-slate-100 flex flex-col justify-between"
      style={{ backgroundColor: '#070913' }}
    >
      {/* Dynamic Cyber Matrix Canvas Engine */}
      <CyberBackground />

      {/* TOP FLOATING ISLAND NAVIGATION HEADER */}
      <header className="sticky top-0 z-30 px-4 sm:px-8 py-3 flex items-center justify-between border-b border-white/[0.07] bg-[#070913]/85 backdrop-blur-xl">
        {/* Left: Brand Identity */}
        <Link
          to="/"
          onClick={() => cyberSound.playClick()}
          className="flex items-center gap-3 group cursor-pointer"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span
                className="font-bold text-sm text-slate-100 tracking-tight"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                AI Chargeback Guardian
              </span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                PROD
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-500">Autonomous Investigation Platform</p>
          </div>
        </Link>

        {/* Center: Segmented Navigation Pill */}
        <nav className="flex items-center p-1 rounded-xl bg-slate-900/80 border border-white/[0.08] shadow-inner font-mono text-xs">
          <NavLink
            to="/"
            end
            onClick={() => cyberSound.playSelect()}
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
              }`
            }
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Command Deck</span>
          </NavLink>

          <NavLink
            to="/analytics"
            onClick={() => cyberSound.playSelect()}
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
              }`
            }
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Benchmark Analytics</span>
          </NavLink>
        </nav>

        {/* Right: Security Pill, Audio & Reviewer Persona Auth */}
        <div className="flex items-center gap-3">
          {/* Grounding Guardrail Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">
            <Lock className="w-3 h-3" />
            <span>ZERO TOKEN FABRICATION</span>
          </div>

          {/* Audio Synthesizer Toggle */}
          <button
            type="button"
            onClick={toggleSound}
            className="p-2 rounded-lg border border-white/[0.08] bg-slate-900/60 hover:bg-slate-800 transition-colors text-slate-400 hover:text-slate-200 cursor-pointer"
            title={audioEnabled ? 'Mute Synth Audio FX' : 'Enable Synth Audio FX'}
          >
            {audioEnabled ? (
              <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
            ) : (
              <VolumeX className="w-3.5 h-3.5" />
            )}
          </button>

          {/* User Profile & Role Switcher Dropdown */}
          <div className="relative" ref={dropdownRef}>
            {user ? (
              <button
                type="button"
                onClick={() => {
                  cyberSound.playClick();
                  setProfileOpen(!profileOpen);
                }}
                className="flex items-center gap-2 p-1.5 pr-2.5 rounded-xl bg-slate-900/90 border border-white/[0.1] hover:border-indigo-500/40 transition-all cursor-pointer text-xs font-mono"
              >
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-indigo-600 to-cyan-600 flex items-center justify-center font-bold text-[10px] text-white">
                  {user.avatarInitials || 'AN'}
                </div>
                <div className="text-left hidden sm:block">
                  <p className="text-[11px] font-bold text-slate-200 leading-tight">
                    {user.name}
                  </p>
                  <p className="text-[9px] text-indigo-400 leading-tight">
                    {user.reviewer_id}
                  </p>
                </div>
                <ChevronDown className="w-3 h-3 text-slate-400 ml-1" />
              </button>
            ) : (
              <Link
                to="/login"
                onClick={() => cyberSound.playClick()}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold transition-all shadow-md shadow-indigo-600/20"
              >
                <KeyRound className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
            )}

            {/* Persona Dropdown Menu */}
            {profileOpen && user && (
              <div
                className="absolute right-0 mt-2 w-72 rounded-2xl p-3 border shadow-2xl z-50 font-mono text-xs backdrop-blur-2xl"
                style={{
                  background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(9, 13, 30, 0.98) 100%)',
                  borderColor: 'rgba(99, 102, 241, 0.3)',
                  boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8)',
                }}
              >
                <div className="pb-3 mb-2 border-b border-slate-800">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">Authenticated Reviewer</span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {user.reviewer_id}
                    </span>
                  </div>
                  <p className="text-sm font-bold text-white mt-1">{user.name}</p>
                  <p className="text-[10px] text-slate-400">{user.email}</p>
                  <p className="text-[10px] text-cyan-400 font-bold mt-1">{user.role}</p>
                </div>

                <div className="space-y-1 mb-2">
                  <p className="text-[10px] text-slate-500 uppercase font-bold px-1 mb-1">
                    1-Click Persona Switcher
                  </p>
                  {DEMO_PERSONAS.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => {
                        loginWithPersona(p.id);
                        setProfileOpen(false);
                      }}
                      className={`w-full p-2 rounded-xl text-left flex items-center justify-between cursor-pointer transition-colors ${
                        user.id === p.id
                          ? 'bg-indigo-600/20 text-indigo-300 font-bold'
                          : 'hover:bg-slate-800/60 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-md bg-slate-800 text-[10px] flex items-center justify-center font-bold text-indigo-400">
                          {p.avatarInitials}
                        </span>
                        <div>
                          <p className="text-[11px] text-slate-200">{p.name}</p>
                          <p className="text-[9px] text-slate-500">{p.role}</p>
                        </div>
                      </div>
                      <span className="text-[9px] text-slate-500">{p.reviewer_id}</span>
                    </button>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                  <Link
                    to="/login"
                    onClick={() => {
                      setProfileOpen(false);
                      cyberSound.playClick();
                    }}
                    className="text-[11px] text-indigo-400 hover:text-cyan-300 flex items-center gap-1 font-bold"
                  >
                    <User className="w-3 h-3" />
                    <span>Login Page</span>
                  </Link>

                  <button
                    type="button"
                    onClick={() => {
                      logout();
                      setProfileOpen(false);
                      navigate('/login');
                    }}
                    className="text-[11px] text-rose-400 hover:text-rose-300 flex items-center gap-1 font-bold cursor-pointer"
                  >
                    <LogOut className="w-3 h-3" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* MAIN VIEWPORT */}
      <main className="flex-1 px-4 sm:px-8 py-6 max-w-[1700px] w-full mx-auto relative z-10">
        <Outlet />
      </main>

      {/* FOOTER LIVE TELEMETRY LOG */}
      <footer className="px-4 sm:px-8 py-3 border-t border-white/[0.07] bg-[#070913]/90 backdrop-blur-xl relative z-10">
        <LiveCyberTicker />
      </footer>
    </div>
  );
}
