import { useState, useEffect } from 'react';
import { Terminal, ShieldCheck, Activity, Cpu, Lock, Sparkles } from 'lucide-react';

const mockLogs = [
  { icon: ShieldCheck, tag: 'INTEGRITY', text: 'SHA-256 evidence bundle verification: 100% authentic', color: '#22c55e' },
  { icon: Activity, tag: 'INFERENCE', text: 'XGBoost & Logistic Regression held-out matrix initialized', color: '#6366f1' },
  { icon: Lock, tag: 'GUARDRAIL', text: 'LLM Hallucination Guardrail: Strict verified evidence constraint active', color: '#06b6d4' },
  { icon: Cpu, tag: 'TELEMETRY', text: 'Synthetic merchant stream monitoring 2,000 baseline cases', color: '#a855f7' },
  { icon: Sparkles, tag: 'SHAP', text: 'SHAP kernel explainer pre-computed on synthetic test set', color: '#eab308' },
];

export default function LiveCyberTicker() {
  const [currentIdx, setCurrentIdx] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % mockLogs.length);
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  const current = mockLogs[currentIdx];
  const Icon = current.icon;

  return (
    <div
      className="rounded-xl px-4 py-2 flex items-center justify-between text-xs overflow-hidden relative"
      style={{
        background: 'rgba(10, 15, 38, 0.75)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        border: '1px solid rgba(99, 102, 241, 0.12)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.35)',
      }}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <Terminal className="w-3.5 h-3.5" style={{ color: '#06b6d4' }} />
          <span className="font-mono text-[10px] font-bold tracking-wider" style={{ color: 'rgba(6, 182, 212, 0.8)' }}>
            SYS://EVENT
          </span>
        </div>

        <div className="h-3 w-px flex-shrink-0" style={{ background: 'rgba(99, 102, 241, 0.2)' }} />

        <div className="flex items-center gap-2 min-w-0 animate-fade-in key={currentIdx}">
          <span
            className="font-mono text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded tracking-widest flex-shrink-0"
            style={{
              background: `${current.color}15`,
              color: current.color,
              border: `1px solid ${current.color}35`,
            }}
          >
            {current.tag}
          </span>
          <span className="truncate font-mono text-[11px]" style={{ color: 'rgba(240, 242, 248, 0.85)' }}>
            {current.text}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 ml-4 flex-shrink-0 font-mono text-[10px]" style={{ color: 'rgba(148, 163, 184, 0.5)' }}>
        <span className="hidden md:inline">LATENCY: 12ms</span>
        <div className="w-1.5 h-1.5 rounded-full animate-ping" style={{ backgroundColor: '#22c55e' }} />
      </div>
    </div>
  );
}
