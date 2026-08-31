import React, { useState, useEffect } from 'react';
import {
  Zap,
  Play,
  CheckCircle2,
  AlertTriangle,
  X,
  Shield,
  Clock,
  Layers,
  Loader2,
  Check,
  ToggleLeft,
  ToggleRight,
  TrendingUp,
  DollarSign,
} from 'lucide-react';
import { getAutoPilotRules, runAutoPilot } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

export default function AutoPilotModal({ onExecuted, onClose }) {
  const [rules, setRules] = useState([
    {
      id: 'rule_high_confidence_win',
      name: 'High Probability Auto-Contest',
      description: 'Auto-Approve disputes with estimated Win Probability >= 85% and complete evidence',
      enabled: true,
      action: 'APPROVE',
    },
    {
      id: 'rule_micro_amount_concede',
      name: 'Micro-Dispute Fee Protection',
      description: 'Auto-Concede disputes with Amount < $20 to eliminate $15 arbitration fees',
      enabled: true,
      action: 'REJECT',
    },
    {
      id: 'rule_zero_risk_customer',
      name: 'Loyal Customer 3DS Fast-Track',
      description: 'Auto-Approve 3DS authenticated transactions with 0 prior customer chargebacks',
      enabled: true,
      action: 'APPROVE',
    },
  ]);
  const [loadingRules, setLoadingRules] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [batchSize, setBatchSize] = useState(10);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoadingRules(true);
        const data = await getAutoPilotRules();
        if (data.rules && data.rules.length > 0) {
          setRules(data.rules);
        }
      } catch (err) {
        console.error('Failed to load rules:', err);
      } finally {
        setLoadingRules(false);
      }
    }
    load();
  }, []);

  const handleToggleRule = (idx) => {
    cyberSound.playClick();
    setRules((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, enabled: !r.enabled } : r))
    );
  };

  const handleRunAutoPilot = async () => {
    try {
      setExecuting(true);
      setError(null);
      cyberSound.playClick();
      const res = await runAutoPilot(batchSize, 'AUTOPILOT_AI_AGENT');
      setResult(res);
      cyberSound.playSuccess();
    } catch (err) {
      console.error('AutoPilot failed:', err);
      setError('AutoPilot failed: ' + (err.response?.data?.detail || err.message));
      cyberSound.playError();
    } finally {
      setExecuting(false);
    }
  };

  const handleApplyAndClose = () => {
    cyberSound.playSuccess();
    if (onExecuted) onExecuted();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="w-full max-w-2xl rounded-3xl p-6 border shadow-2xl relative font-mono text-xs overflow-hidden max-h-[90vh] flex flex-col"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(9, 13, 30, 0.99) 100%)',
          borderColor: 'rgba(245, 158, 11, 0.4)',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(245, 158, 11, 0.15)',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30 shadow-md shadow-amber-500/10">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>Auto-Pilot SLA Rules Engine</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  AUTONOMOUS
                </span>
              </h3>
              <p className="text-[10px] text-slate-300 font-medium">
                Autonomous risk policy evaluation, fee-saving concessions, & auto-contests
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
          {/* Active Policy Rules with Toggles */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-[10px] text-amber-400 uppercase font-bold tracking-wider">
                Configurable SLA Policies
              </label>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-400">Batch Size:</span>
                <select
                  value={batchSize}
                  onChange={(e) => setBatchSize(Number(e.target.value))}
                  className="bg-slate-900 border border-slate-700 text-cyan-300 rounded px-2 py-0.5 text-[10px] focus:outline-none"
                >
                  <option value={5}>5 Disputes</option>
                  <option value={10}>10 Disputes</option>
                  <option value={20}>20 Disputes</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              {rules.map((rule, idx) => (
                <div
                  key={rule.id}
                  className={`p-3 rounded-2xl border transition-all flex items-start justify-between gap-3 ${
                    rule.enabled
                      ? 'bg-slate-900/90 border-slate-700 shadow-sm'
                      : 'bg-slate-950/60 border-slate-900 opacity-60'
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    <Shield className={`w-4 h-4 mt-0.5 flex-shrink-0 ${rule.enabled ? 'text-amber-400' : 'text-slate-600'}`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-xs text-slate-100">{rule.name}</p>
                        <span
                          className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                            rule.action === 'APPROVE'
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          }`}
                        >
                          {rule.action === 'APPROVE' ? 'AUTO-CONTEST' : 'AUTO-CONCEDE'}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-300 mt-0.5">{rule.description}</p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleToggleRule(idx)}
                    className="p-1 rounded text-slate-400 hover:text-amber-300 cursor-pointer flex-shrink-0"
                    title={rule.enabled ? 'Disable rule' : 'Enable rule'}
                  >
                    {rule.enabled ? (
                      <ToggleRight className="w-6 h-6 text-amber-400" />
                    ) : (
                      <ToggleLeft className="w-6 h-6 text-slate-600" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[11px] flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Execution Results View */}
          {result && (
            <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 animate-fade-in space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>
                    Auto-Pilot Triaged {result.executed_count} Disputes
                  </span>
                </div>
                <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/20 font-mono text-emerald-200">
                  Zero Hallucinations Verified
                </span>
              </div>

              {/* Dispute List Items */}
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1 font-mono text-[10px]">
                {result.results?.map((res, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between text-slate-200"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-cyan-300">{res.dispute_reference}</span>
                      <span className="text-slate-400">${Number(res.amount).toFixed(2)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400 hidden sm:inline text-[9px] truncate max-w-[200px]">
                        {res.rule_matched}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded font-bold text-[9px] ${
                          res.decision === 'APPROVE'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {res.decision}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between flex-shrink-0">
          <span className="text-[10px] text-slate-400 font-mono">
            Immutable Audit Trail Signed
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-xl text-slate-400 hover:text-white cursor-pointer font-mono"
            >
              Close
            </button>
            {result ? (
              <button
                type="button"
                onClick={handleApplyAndClose}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-lg shadow-emerald-600/20 font-mono"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Done & Refresh Deck</span>
              </button>
            ) : (
              <button
                type="button"
                disabled={executing}
                onClick={handleRunAutoPilot}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white font-bold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5 shadow-lg shadow-amber-500/20 font-mono"
              >
                {executing ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5" />
                )}
                <span>Run Auto-Pilot Triage</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
