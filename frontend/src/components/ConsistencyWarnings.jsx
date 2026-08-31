import React from 'react';
import { AlertTriangle, AlertOctagon, CheckCircle2, ShieldCheck, Info } from 'lucide-react';

export default function ConsistencyWarnings({ warnings = [] }) {
  if (warnings.length === 0) {
    return (
      <div className="p-3.5 rounded-xl bg-emerald-950/15 border border-emerald-500/25 flex items-center justify-between font-mono text-xs">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <div>
            <p className="font-bold text-emerald-300 text-xs">
              EVIDENCE INTEGRITY AUDIT PASSED
            </p>
            <p className="text-[10px] text-emerald-400/80">
              Zero conflicting timestamps, missing required amounts, or relational anomalies detected.
            </p>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
          7/7 CHECKS OK
        </span>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <h4 className="font-bold text-amber-300 text-xs">
            DATA CONSISTENCY WARNINGS ({warnings.length})
          </h4>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
          AUDIT ANOMALIES
        </span>
      </div>

      <div className="space-y-2">
        {warnings.map((w, idx) => {
          const isCritical = w.severity === 'CRITICAL';

          return (
            <div
              key={w.code || idx}
              className={`p-3 rounded-lg border flex items-start gap-2.5 ${
                isCritical
                  ? 'bg-red-950/30 border-red-500/40 text-red-300'
                  : 'bg-amber-950/30 border-amber-500/30 text-amber-300'
              }`}
            >
              {isCritical ? (
                <AlertOctagon className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              ) : (
                <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              )}
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[11px] uppercase tracking-wider text-slate-100">
                    {w.code}
                  </span>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                      isCritical
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {w.severity}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Field: {w.field}
                  </span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {w.message}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
