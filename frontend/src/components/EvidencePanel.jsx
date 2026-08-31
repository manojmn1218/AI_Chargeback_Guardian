import { CheckCircle2, XCircle, AlertCircle, Database, ShieldCheck, Lock, Hash } from 'lucide-react';
import CyberCard from './CyberCard';

/**
 * EvidencePanel — Cyber Evidence Verification Engine.
 * Visualizes 7 core evidence categories with cryptographically-styled verification checks.
 */
export default function EvidencePanel({ title = "Evidence Matrix", items = [], delay = 100 }) {
  if (items.length === 0) {
    return (
      <CyberCard delay={delay} className="p-6" glowColor="rgba(99, 102, 241, 0.2)">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.2)',
                boxShadow: '0 0 14px rgba(99, 102, 241, 0.2)',
              }}
            >
              <Database className="w-4 h-4" style={{ color: '#818cf8' }} />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-wide" style={{ color: '#f8fafc' }}>
                {title}
              </h3>
              <p className="text-[10px] font-mono" style={{ color: 'rgba(148, 163, 184, 0.5)' }}>
                7 MANDATORY CATEGORIES ENGINE
              </p>
            </div>
          </div>

          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full font-mono text-[10px] font-bold"
            style={{
              background: 'rgba(99, 102, 241, 0.08)',
              color: '#a5b4fc',
              border: '1px solid rgba(99, 102, 241, 0.15)',
            }}
          >
            <Lock className="w-3 h-3" />
            <span>UNGROUNDED TOKENS BLOCKED</span>
          </div>
        </div>

        {/* Diagnostic Holographic Empty State */}
        <div
          className="flex flex-col items-center justify-center py-10 px-4 rounded-xl relative overflow-hidden"
          style={{
            background: 'rgba(8, 12, 32, 0.5)',
            border: '1px dashed rgba(99, 102, 241, 0.15)',
          }}
        >
          {/* Subtle radar pulse in background */}
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center mb-3 animate-pulse"
            style={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(6, 182, 212, 0.1))',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.15)',
            }}
          >
            <ShieldCheck className="w-6 h-6" style={{ color: '#06b6d4' }} />
          </div>

          <p className="text-xs font-bold tracking-wide mb-1" style={{ color: '#e2e8f0' }}>
            Evidence Engine Standby
          </p>
          <p className="text-[11px] text-center font-mono max-w-sm" style={{ color: 'rgba(148, 163, 184, 0.6)' }}>
            Retrieval layer will verify Payment, Invoice, Order, Delivery, Refund, Communication, and Policy documents on case ingestion.
          </p>
        </div>
      </CyberCard>
    );
  }

  const available = items.filter((i) => i.available).length;
  const total = items.length;
  const percentage = Math.round((available / total) * 100);
  const isHighCompleteness = percentage >= 75;

  return (
    <CyberCard delay={delay} className="p-6" glowColor={isHighCompleteness ? 'rgba(34, 197, 94, 0.2)' : 'rgba(245, 158, 11, 0.2)'}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center"
            style={{
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
            }}
          >
            <Database className="w-4 h-4" style={{ color: '#818cf8' }} />
          </div>
          <div>
            <h3 className="text-sm font-bold tracking-wide" style={{ color: '#f8fafc' }}>
              {title}
            </h3>
            <p className="text-[10px] font-mono" style={{ color: 'rgba(148, 163, 184, 0.5)' }}>
              {available}/{total} CATEGORIES VERIFIED
            </p>
          </div>
        </div>

        <div
          className="flex items-center gap-2 px-3 py-1 rounded-full font-mono text-[11px] font-extrabold"
          style={{
            background: isHighCompleteness ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            color: isHighCompleteness ? '#4ade80' : '#fbbf24',
            border: `1px solid ${isHighCompleteness ? 'rgba(34, 197, 94, 0.25)' : 'rgba(245, 158, 11, 0.25)'}`,
            boxShadow: `0 0 12px ${isHighCompleteness ? 'rgba(34, 197, 94, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`,
          }}
        >
          <span>{percentage}% COMPLETE</span>
        </div>
      </div>

      {/* High-Tech Progress Bar */}
      <div className="mb-5">
        <div
          className="h-2 rounded-full overflow-hidden p-[1px] relative"
          style={{
            background: 'rgba(15, 20, 50, 0.8)',
            border: '1px solid rgba(99, 102, 241, 0.15)',
          }}
        >
          <div
            className="h-full rounded-full transition-all duration-1000 relative"
            style={{
              width: `${percentage}%`,
              background: isHighCompleteness
                ? 'linear-gradient(90deg, #10b981, #06b6d4)'
                : 'linear-gradient(90deg, #f59e0b, #eab308)',
              boxShadow: isHighCompleteness
                ? '0 0 14px rgba(6, 182, 212, 0.6)'
                : '0 0 14px rgba(245, 158, 11, 0.6)',
            }}
          >
            {/* Shimmer on progress bar */}
            <div
              className="absolute inset-0 shimmer opacity-50"
              style={{
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
              }}
            />
          </div>
        </div>
      </div>

      {/* Evidence Items List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        {items.map((item, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-3 rounded-xl transition-all duration-200 hover:scale-[1.01]"
            style={{
              background: item.available
                ? 'rgba(34, 197, 94, 0.04)'
                : 'rgba(239, 68, 68, 0.04)',
              border: `1px solid ${
                item.available ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)'
              }`,
            }}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              {item.available ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" style={{ color: '#4ade80', filter: 'drop-shadow(0 0 6px rgba(34, 197, 94, 0.4))' }} />
              ) : (
                <XCircle className="w-4 h-4 flex-shrink-0" style={{ color: '#f87171', filter: 'drop-shadow(0 0 6px rgba(239, 68, 68, 0.4))' }} />
              )}
              <div className="truncate">
                <p className="text-xs font-semibold truncate" style={{ color: '#f8fafc' }}>
                  {item.name}
                </p>
                <p className="text-[10px] font-mono" style={{ color: 'rgba(148, 163, 184, 0.5)' }}>
                  {item.source || (item.available ? 'Verified' : 'Missing')}
                </p>
              </div>
            </div>

            <span
              className="font-mono text-[9px] font-bold uppercase px-2 py-0.5 rounded flex-shrink-0"
              style={{
                background: item.available ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                color: item.available ? '#4ade80' : '#f87171',
                border: `1px solid ${item.available ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
              }}
            >
              {item.available ? 'ATTACHED' : 'REQUIRED'}
            </span>
          </div>
        ))}
      </div>
    </CyberCard>
  );
}
