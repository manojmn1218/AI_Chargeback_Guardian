import React, { useState, useEffect } from 'react';
import { Zap, Play, CheckCircle2, AlertTriangle, X, Shield, Clock, Layers, Loader2 } from 'lucide-react';
import { getAutoPilotRules, runAutoPilot } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

export default function AutoPilotModal({ onExecuted, onClose }) {
  const [rules, setRules] = useState([]);
  const [loadingRules, setLoadingRules] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoadingRules(true);
        const data = await getAutoPilotRules();
        setRules(data.rules || []);
      } catch (err) {
        console.error('Failed to load rules:', err);
      } finally {
        setLoadingRules(false);
      }
    }
    load();
  }, []);

  const handleRunAutoPilot = async () => {
    try {
      setExecuting(true);
      setError(null);
      cyberSound.playClick();
      const res = await runAutoPilot(15, 'AUTOPILOT_AI_AGENT');
      setResult(res);
      cyberSound.playSuccess();
      setTimeout(() => {
        onExecuted();
      }, 1800);
    } catch (err) {
      console.error('AutoPilot failed:', err);
      setError('AutoPilot failed: ' + (err.response?.data?.detail || err.message));
      cyberSound.playError();
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="w-full max-w-xl rounded-3xl p-6 border shadow-2xl relative font-mono text-xs overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(9, 13, 30, 0.99) 100%)',
          borderColor: 'rgba(99, 102, 241, 0.4)',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.15)',
        }}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Auto-Pilot SLA Rules Engine</h3>
              <p className="text-[10px] text-slate-400">Autonomous risk policy evaluation & auto-contesting</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Active Policy Rules */}
        <div className="mt-4">
          <label className="text-[10px] text-slate-400 uppercase font-bold block mb-2">
            Active Risk Operations SLA Policies
          </label>
          <div className="space-y-2">
            {loadingRules ? (
              <div className="py-6 text-center text-slate-500">
                <Loader2 className="w-4 h-4 animate-spin mx-auto mb-1 text-amber-400" />
                Loading rules...
              </div>
            ) : (
              rules.map((rule) => (
                <div
                  key={rule.id}
                  className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-start justify-between gap-3"
                >
                  <div className="flex items-start gap-2.5">
                    <Shield className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-bold text-xs text-slate-200">{rule.name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{rule.description}</p>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      rule.action === 'APPROVE'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}
                  >
                    {rule.action}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {error && <p className="text-[11px] text-rose-400 mt-2">{error}</p>}

        {result && (
          <div className="mt-4 p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 animate-fade-in">
            <div className="flex items-center gap-2 font-bold mb-1">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>
                Auto-Pilot Executed: {result.executed_count} / {result.evaluated_count} disputes authorized
              </span>
            </div>
            <p className="text-[10px] text-slate-300">
              Evaluated against zero-hallucination groundings and logged to immutable audit trail.
            </p>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Autonomous Gate Active</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-xl text-slate-400 hover:text-white cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={executing || !!result}
              onClick={handleRunAutoPilot}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white font-bold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
            >
              {executing ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5" />
              )}
              <span>Run Auto-Pilot Triage</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
