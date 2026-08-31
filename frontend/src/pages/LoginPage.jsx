import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, DEMO_PERSONAS } from '../context/AuthContext';
import { cyberSound } from '../utils/cyberSound';
import CyberBackground from '../components/CyberBackground';
import {
  Shield,
  Lock,
  UserCheck,
  KeyRound,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Cpu,
  Fingerprint,
} from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { user, loginWithPersona, loginWithCredentials } = useAuth();

  const [email, setEmail] = useState('alex.vance@chargeback-guardian.ai');
  const [password, setPassword] = useState('••••••••••••');
  const [selectedPersonaId, setSelectedPersonaId] = useState('analyst_senior');
  const [isLoading, setIsLoading] = useState(false);

  const handlePersonaSelect = (persona) => {
    setSelectedPersonaId(persona.id);
    setEmail(persona.email);
    setPassword('••••••••••••');
    cyberSound.playSelect();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    cyberSound.playClick();

    setTimeout(() => {
      loginWithCredentials(email, password);
      setIsLoading(false);
      navigate('/');
    }, 400);
  };

  const handleQuickLogin = (personaId) => {
    setIsLoading(true);
    loginWithPersona(personaId);
    setTimeout(() => {
      setIsLoading(false);
      navigate('/');
    }, 200);
  };

  return (
    <div
      className="min-h-screen relative font-sans text-slate-100 flex flex-col justify-between items-center p-4 sm:p-8"
      style={{ backgroundColor: '#070913' }}
    >
      <CyberBackground />

      {/* TOP HEADER */}
      <header className="w-full max-w-5xl flex items-center justify-between relative z-10 py-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight flex items-center gap-2">
              <span>AI Chargeback Guardian</span>
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                PROD GATEWAY
              </span>
            </h1>
            <p className="text-[10px] font-mono text-slate-500">Autonomous Risk & Investigation Platform</p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-xl">
          <Fingerprint className="w-3.5 h-3.5" />
          <span>FIDO2 / 2FA ENFORCED</span>
        </div>
      </header>

      {/* MAIN AUTHENTICATION CARD */}
      <div className="w-full max-w-md relative z-10 my-auto">
        <div
          className="rounded-3xl p-6 sm:p-8 border shadow-2xl relative overflow-hidden backdrop-blur-2xl"
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(9, 13, 30, 0.95) 100%)',
            borderColor: 'rgba(99, 102, 241, 0.25)',
            boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.1)',
          }}
        >
          {/* Top Cyber Accent Line */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400" />

          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 mb-3">
              <Lock className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Risk Analyst Sign In
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select a demo reviewer persona or enter risk credentials
            </p>
          </div>

          {/* 1-CLICK QUICK PERSONA SWITCHER */}
          <div className="space-y-2 mb-6">
            <label className="block text-[10px] font-mono uppercase font-bold text-slate-400">
              1-Click Demo Reviewer Persona
            </label>
            <div className="space-y-2 font-mono text-xs">
              {DEMO_PERSONAS.map((p) => {
                const isSelected = selectedPersonaId === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => handlePersonaSelect(p)}
                    className={`w-full p-2.5 rounded-xl border text-left flex items-center justify-between cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-600/15 border-indigo-500 text-white shadow-md shadow-indigo-600/15'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-[11px] font-bold text-indigo-400">
                        {p.avatarInitials}
                      </div>
                      <div>
                        <div className="font-bold text-slate-200 text-xs flex items-center gap-1.5">
                          <span>{p.name}</span>
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                            {p.reviewer_id}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500">{p.role}</p>
                      </div>
                    </div>

                    {isSelected ? (
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                    ) : (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuickLogin(p.id);
                        }}
                        className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-indigo-400 hover:text-white hover:bg-indigo-600 transition-colors"
                      >
                        Enter →
                      </button>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* CREDENTIALS FORM */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[10px] font-mono uppercase font-bold text-slate-400 mb-1">
                Security Identifier / Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                  placeholder="analyst@guardian.ai"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-mono uppercase font-bold text-slate-400 mb-1">
                Password / Passkey
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-xs font-mono cursor-pointer flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <KeyRound className="w-3.5 h-3.5" />
                  <span>Authenticate Session</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* FOOTER NOTICE */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 text-center">
            <p className="text-[10px] font-mono text-slate-500 flex items-center justify-center gap-1.5">
              <Cpu className="w-3 h-3 text-cyan-400" />
              <span>Immutable Audit Logger Active • Session Secured</span>
            </p>
          </div>
        </div>
      </div>

      {/* BOTTOM FOOTER */}
      <footer className="w-full max-w-5xl text-center py-4 text-[10px] font-mono text-slate-600 relative z-10">
        AI Chargeback Guardian v0.1.0 • Evaluator Demo Mode Active
      </footer>
    </div>
  );
}
