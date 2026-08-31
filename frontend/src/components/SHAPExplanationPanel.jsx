import React, { useState, useEffect } from 'react';
import {
  Brain,
  TrendingUp,
  TrendingDown,
  Info,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import CyberCard from './CyberCard';
import { getDisputeExplanation } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

export default function SHAPExplanationPanel({ disputeId }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAllFeatures, setShowAllFeatures] = useState(false);

  useEffect(() => {
    fetchExplanation();
  }, [disputeId]);

  async function fetchExplanation() {
    try {
      setLoading(true);
      setError(null);
      const data = await getDisputeExplanation(disputeId);
      setExplanation(data);
    } catch (err) {
      console.error('Failed to load SHAP explanation:', err);
      setError(err.response?.data?.detail || 'Failed to load model explainability');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <CyberCard title="AI EXPLAINABILITY (TreeSHAP)" icon={Brain} glowColor="indigo">
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="relative w-12 h-12">
            <div className="absolute inset-0 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
            <Brain className="w-6 h-6 text-indigo-400 absolute inset-0 m-auto animate-pulse" />
          </div>
          <span className="text-xs font-mono text-slate-400">Computing TreeSHAP feature attributions...</span>
        </div>
      </CyberCard>
    );
  }

  if (error) {
    return (
      <CyberCard title="AI EXPLAINABILITY (TreeSHAP)" icon={Brain} glowColor="rose">
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchExplanation}
            className="px-3 py-1 bg-rose-900/60 hover:bg-rose-800 text-white rounded text-xs"
          >
            Retry
          </button>
        </div>
      </CyberCard>
    );
  }

  if (!explanation) return null;

  const {
    score,
    classification,
    prediction_probability,
    base_value,
    top_positive_factors = [],
    top_negative_factors = [],
    features = [],
    method,
    disclaimer,
  } = explanation;

  // Maximum absolute contribution for proportional bar width
  const maxContrib = Math.max(
    ...features.map((f) => Math.abs(f.contribution)),
    0.01
  );

  return (
    <div className="space-y-6 font-sans">
      {/* 1. Header Overview Card */}
      <CyberCard title="MODEL EXPLAINABILITY & FEATURE ATTRIBUTION" icon={Brain} glowColor="indigo">
        <div className="space-y-6">
          {/* Top Score Banner */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800 font-mono">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Case Strength Score</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span
                  className={`text-3xl font-black ${
                    score >= 70
                      ? 'text-emerald-400'
                      : score >= 40
                      ? 'text-amber-400'
                      : 'text-rose-400'
                  }`}
                >
                  {score}
                </span>
                <span className="text-xs text-slate-500">/ 100</span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ml-2 ${
                    score >= 70
                      ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                      : score >= 40
                      ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                      : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                  }`}
                >
                  {classification}
                </span>
              </div>
            </div>

            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Win Probability</span>
              <div className="text-2xl font-black text-white mt-1">
                {(prediction_probability * 100).toFixed(1)}%
              </div>
              <span className="text-[10px] text-slate-400">Baseline distribution: {(base_value * 100).toFixed(1)}%</span>
            </div>

            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Attribution Engine</span>
              <div className="flex items-center gap-1.5 mt-1 text-xs font-bold text-cyan-300">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{method === 'SHAP' ? 'TreeSHAP (Exact Tree Attribution)' : 'Model Feature Importance'}</span>
              </div>
              <span className="text-[10px] text-slate-500">Evaluated on {features.length} model features</span>
            </div>
          </div>

          {/* 2. Top Drivers Split: Positive vs Negative */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Positive Drivers */}
            <div className="p-4 rounded-xl bg-emerald-950/10 border border-emerald-500/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold">
                  <TrendingUp className="w-4 h-4" />
                  <span>POSITIVE CONTRIBUTING FACTORS</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400/80 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Increases Win Probability
                </span>
              </div>

              <div className="space-y-2.5">
                {top_positive_factors.length === 0 ? (
                  <div className="text-xs font-mono text-slate-500 italic py-2">No strong positive drivers detected.</div>
                ) : (
                  top_positive_factors.map((factor, idx) => {
                    const widthPct = Math.min(100, Math.max(12, (Math.abs(factor.contribution) / maxContrib) * 100));
                    return (
                      <div key={idx} className="space-y-1">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-slate-200 font-semibold flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                            {factor.display_name}
                          </span>
                          <span className="text-emerald-400 font-bold">{factor.impact_pct}</span>
                        </div>
                        <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-emerald-500 to-teal-400 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${widthPct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Negative Drivers */}
            <div className="p-4 rounded-xl bg-rose-950/10 border border-rose-500/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-rose-400 font-mono text-xs font-bold">
                  <TrendingDown className="w-4 h-4" />
                  <span>NEGATIVE CONTRIBUTING FACTORS</span>
                </div>
                <span className="text-[10px] font-mono text-rose-400/80 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                  Increases Dispute Risk
                </span>
              </div>

              <div className="space-y-2.5">
                {top_negative_factors.length === 0 ? (
                  <div className="text-xs font-mono text-slate-500 italic py-2">No significant negative risk factors.</div>
                ) : (
                  top_negative_factors.map((factor, idx) => {
                    const widthPct = Math.min(100, Math.max(12, (Math.abs(factor.contribution) / maxContrib) * 100));
                    return (
                      <div key={idx} className="space-y-1">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-slate-200 font-semibold flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                            {factor.display_name}
                          </span>
                          <span className="text-rose-400 font-bold">{factor.impact_pct}</span>
                        </div>
                        <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-rose-500 to-amber-500 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${widthPct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* 3. Toggle All Evaluated Features */}
          <div className="pt-2">
            <button
              onClick={() => {
                cyberSound.playClick();
                setShowAllFeatures(!showAllFeatures);
              }}
              className="flex items-center gap-2 text-xs font-mono text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{showAllFeatures ? 'Hide Extended Feature Waterfall' : `View All ${features.length} Evaluated Features`}</span>
            </button>

            {showAllFeatures && (
              <div className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs max-h-96 overflow-y-auto">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">
                  Complete Local Waterfall Attribution Matrix
                </div>
                <div className="space-y-2">
                  {features.map((feat, idx) => {
                    const isPos = feat.direction === 'positive';
                    const widthPct = Math.min(100, Math.max(6, (Math.abs(feat.contribution) / maxContrib) * 100));
                    return (
                      <div key={idx} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between gap-4">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between">
                            <span className="text-slate-300 font-medium truncate">{feat.display_name}</span>
                            {feat.value !== null && feat.value !== undefined && (
                              <span className="text-[10px] text-slate-500 ml-2">Value: {String(feat.value)}</span>
                            )}
                          </div>
                          <div className="w-full bg-slate-950 rounded-full h-1 mt-1 overflow-hidden">
                            <div
                              className={`h-1 rounded-full ${
                                isPos ? 'bg-emerald-400' : 'bg-rose-400'
                              }`}
                              style={{ width: `${widthPct}%` }}
                            />
                          </div>
                        </div>
                        <span
                          className={`text-xs font-bold flex-shrink-0 ${
                            isPos ? 'text-emerald-400' : 'text-rose-400'
                          }`}
                        >
                          {feat.impact_pct}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* 4. Compliance Disclaimer Banner */}
          <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 flex items-start gap-2.5 text-[11px] font-mono text-indigo-300/90 leading-relaxed">
            <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-white font-bold">Legal & Technical Disclosure: </strong>
              {disclaimer}
            </div>
          </div>
        </div>
      </CyberCard>
    </div>
  );
}
