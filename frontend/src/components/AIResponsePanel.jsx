import { useState, useEffect } from 'react';
import {
  Brain,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  RefreshCw,
  Edit3,
  Save,
  Lock,
  Layers,
  FileText,
  Info,
  ChevronDown,
  ChevronUp,
  Cpu,
  Award,
} from 'lucide-react';
import CyberCard from './CyberCard';
import { generateAIResponse } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

export default function AIResponsePanel({ disputeId, initialInvestigation }) {
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [draftText, setDraftText] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showGroundingDetails, setShowGroundingDetails] = useState(false);
  const [showConfidenceBreakdown, setShowConfidenceBreakdown] = useState(false);

  useEffect(() => {
    if (disputeId) {
      loadAIResponse(false);
    }
  }, [disputeId]);

  async function loadAIResponse(forceRefresh = false) {
    try {
      setLoading(true);
      setError(null);
      cyberSound.playClick();
      const result = await generateAIResponse(disputeId, { force_refresh: forceRefresh });
      setAiData(result);
      setDraftText(result.draft_response || '');
      cyberSound.playSuccess();
    } catch (err) {
      console.error('Failed to generate AI response:', err);
      setError(err.response?.data?.detail || err.message || 'AI Response generation failed.');
    } finally {
      setLoading(false);
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(draftText);
    cyberSound.playSuccess();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerate = () => {
    loadAIResponse(true);
  };

  const toggleEdit = () => {
    cyberSound.playClick();
    setIsEditing(!isEditing);
  };

  if (loading && !aiData) {
    return (
      <CyberCard className="p-12 text-center font-mono text-xs text-slate-400 space-y-4">
        <div className="relative w-12 h-12 mx-auto">
          <Brain className="w-12 h-12 text-indigo-400 animate-pulse" />
          <RefreshCw className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto animate-spin" />
        </div>
        <p className="text-white font-bold text-sm">Grounded AI Response Engine Active</p>
        <p className="text-slate-400 text-xs">
          Synthesizing evidence-grounded rebuttal strictly from verified SQLite records...
        </p>
      </CyberCard>
    );
  }

  if (error && !aiData) {
    return (
      <CyberCard className="p-8 text-center font-mono text-xs text-slate-400 space-y-4 border-red-500/40">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto" />
        <h4 className="text-white font-bold">AI Generation Service Error</h4>
        <p className="text-red-300">{error}</p>
        <button
          onClick={() => loadAIResponse(true)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all inline-flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Generation</span>
        </button>
      </CyberCard>
    );
  }

  if (!aiData) return null;

  const isContest = aiData.recommended_action === 'CONTEST';
  const isReview = aiData.recommended_action === 'REVIEW';
  const isAccept = aiData.recommended_action === 'ACCEPT';
  const isGroundingVerified = aiData.grounding_status === 'VERIFIED';
  const confidenceScore = aiData.confidence?.confidence_score || 0;
  const confidenceLevel = aiData.confidence?.confidence_level || 'MEDIUM';

  return (
    <div className="space-y-6 font-mono">
      {/* 1. TOP AI CASE ASSESSMENT BANNER */}
      <div
        className="p-5 sm:p-6 rounded-2xl relative overflow-hidden border"
        style={{
          background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%)',
          borderColor: isGroundingVerified ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)',
        }}
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                <Brain className="w-3.5 h-3.5 text-cyan-400" />
                STEP 5 GROUNDED AI ENGINE
              </span>

              {aiData.is_fallback ? (
                <span className="px-2.5 py-1 rounded-md text-[10px] font-extrabold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                  <Cpu className="w-3 h-3" />
                  DEMO MODE — DETERMINISTIC REBUTTAL ENGINE
                </span>
              ) : (
                <span className="px-2.5 py-1 rounded-md text-[10px] font-extrabold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <Cpu className="w-3 h-3" />
                  {aiData.provider.toUpperCase()} ENGINE ({aiData.model || 'DEFAULT'})
                </span>
              )}

              <span
                className={`px-2.5 py-1 rounded-md text-[10px] font-extrabold flex items-center gap-1 border ${
                  isGroundingVerified
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}
              >
                {isGroundingVerified ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                GROUNDING: {aiData.grounding_status}
              </span>
            </div>

            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              AI Case Assessment & Formal Draft
            </h3>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              {aiData.case_summary}
            </p>
          </div>

          {/* Telemetry Gauges */}
          <div className="flex flex-wrap items-center gap-3 sm:gap-4 font-mono">
            {/* Recommendation Gauge */}
            <div
              className={`p-3 px-4 rounded-xl border text-center min-w-[120px] ${
                isContest
                  ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                  : isReview
                  ? 'bg-amber-950/40 border-amber-500/40 text-amber-300'
                  : 'bg-red-950/40 border-red-500/40 text-red-300'
              }`}
            >
              <p className="text-[9px] uppercase font-bold text-slate-400">AI Recommendation</p>
              <p className="text-base font-black tracking-wide mt-0.5">
                {aiData.recommended_action}
              </p>
            </div>

            {/* Confidence Score Gauge */}
            <div
              onClick={() => setShowConfidenceBreakdown(!showConfidenceBreakdown)}
              className="p-3 px-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center min-w-[120px] cursor-pointer hover:border-cyan-500/50 transition-colors group"
            >
              <p className="text-[9px] uppercase font-bold text-slate-400 flex items-center justify-center gap-1">
                <span>Confidence</span>
                <Info className="w-2.5 h-2.5 text-cyan-400 group-hover:scale-110 transition-transform" />
              </p>
              <p
                className={`text-base font-black tracking-wide mt-0.5 ${
                  confidenceScore >= 80
                    ? 'text-emerald-400'
                    : confidenceScore >= 50
                    ? 'text-amber-400'
                    : 'text-red-400'
                }`}
              >
                {confidenceScore}/100 <span className="text-[10px] text-slate-400 font-bold">({confidenceLevel})</span>
              </p>
            </div>

            {/* Evidence Coverage Gauge */}
            <div className="p-3 px-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center min-w-[120px]">
              <p className="text-[9px] uppercase font-bold text-slate-400">Coverage</p>
              <p className="text-base font-black text-cyan-400 mt-0.5">
                {aiData.evidence_summary?.availability_percentage || 0}%
              </p>
            </div>
          </div>
        </div>

        {/* Confidence Breakdown Drawer */}
        {showConfidenceBreakdown && (
          <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs space-y-3 bg-slate-950/70 p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan-300 uppercase flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" />
                Deterministic Confidence Score Breakdown
              </span>
              <button
                onClick={() => setShowConfidenceBreakdown(false)}
                className="text-slate-500 hover:text-slate-300 text-[10px]"
              >
                Close
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-[11px]">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Evidence Availability (30%)</span>
                <span className="font-bold text-slate-100">{aiData.confidence?.factors?.evidence_availability_pct}%</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Evidence Verification (30%)</span>
                <span className="font-bold text-emerald-400">{aiData.confidence?.factors?.evidence_verification_pct}%</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Grounding Validation (20%)</span>
                <span className="font-bold text-indigo-300">{aiData.confidence?.factors?.grounding_validation_status}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">ML Win Probability (20%)</span>
                <span className="font-bold text-cyan-400">{aiData.confidence?.factors?.ml_win_probability}%</span>
              </div>
            </div>
            <p className="text-[10px] text-slate-500 italic">
              {aiData.confidence?.disclaimer}
            </p>
          </div>
        )}
      </div>

      {/* 2. REASONING & VERIFIED FACTS / MISSING DISCLOSURES GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 text-xs">
        {/* Left: Key Verified Facts */}
        <CyberCard className="p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h4 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 uppercase">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              KEY VERIFIED FACTS ({aiData.key_verified_facts?.length || 0})
            </h4>
            <span className="text-[10px] text-slate-500">Authoritative Data</span>
          </div>

          <div className="space-y-2">
            {aiData.key_verified_facts?.map((fact, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-950/60 border border-emerald-500/20 text-slate-200 text-[11px] leading-relaxed flex items-start gap-2"
              >
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>{fact}</span>
              </div>
            ))}
          </div>
        </CyberCard>

        {/* Right: Missing Information & Conflicts */}
        <CyberCard className="p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5 uppercase">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              MISSING INFORMATION & AUDIT DISCLOSURES
            </h4>
            <span className="text-[10px] text-slate-500">Anti-Hallucination Disclosures</span>
          </div>

          <div className="space-y-2">
            {aiData.missing_information?.length > 0 ? (
              aiData.missing_information.map((item, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-slate-950/60 border border-amber-500/20 text-slate-300 text-[11px] leading-relaxed flex items-start gap-2"
                >
                  <span className="text-amber-400 font-bold mt-0.5">⚠</span>
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <div className="p-3 text-slate-500 text-[11px] italic">
                All 7 required evidence categories are present.
              </div>
            )}

            {aiData.conflicting_information?.map((conflict, idx) => (
              <div
                key={`conf-${idx}`}
                className="p-2.5 rounded-lg bg-red-950/20 border border-red-500/30 text-red-300 text-[11px] leading-relaxed flex items-start gap-2"
              >
                <span className="text-red-400 font-bold mt-0.5">✕</span>
                <span>Consistency Warning: {conflict}</span>
              </div>
            ))}
          </div>
        </CyberCard>
      </div>

      {/* 3. AI-GENERATED FORMAL DRAFT REBUTTAL */}
      <CyberCard className="p-5 sm:p-6 space-y-4" glowColor="rgba(99, 102, 241, 0.25)">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-300 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white uppercase tracking-wide">
                AI-GENERATED FORMAL REBUTTAL DRAFT
              </h4>
              <p className="text-[10px] text-slate-400">
                Grounding-enforced statement with verifiable database citations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleEdit}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                isEditing
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
              }`}
            >
              {isEditing ? <Save className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
              <span>{isEditing ? 'Editing Mode' : 'Edit Draft'}</span>
            </button>

            <button
              onClick={handleRegenerate}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-bold transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
              <span>Regenerate</span>
            </button>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied to Clipboard' : 'Copy Rebuttal'}</span>
            </button>
          </div>
        </div>

        {/* Draft Text Area */}
        <div className="relative">
          <textarea
            value={draftText}
            onChange={(e) => setDraftText(e.target.value)}
            disabled={!isEditing}
            rows={15}
            className={`w-full p-4 rounded-xl font-mono text-xs leading-relaxed transition-all resize-y ${
              isEditing
                ? 'bg-slate-950 text-slate-100 border border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-400 shadow-inner'
                : 'bg-slate-950/70 text-slate-300 border border-slate-800/80 cursor-default'
            }`}
          />
          {isEditing && (
            <div className="absolute top-3 right-3 text-[10px] text-amber-400 font-bold bg-amber-950/80 px-2 py-0.5 rounded border border-amber-500/40">
              Live Human Edit Mode
            </div>
          )}
        </div>

        {/* 4. TRACEABLE EVIDENCE CITATIONS CHIPS */}
        <div className="pt-2 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              REFERENCED EVIDENCE CITATIONS ({aiData.evidence_references?.length || 0})
            </span>
            <span className="text-[10px] text-slate-500">Directly Traceable to Database</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {aiData.evidence_references?.map((ref, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-slate-900 border border-cyan-500/30 text-cyan-300 hover:border-cyan-400 transition-colors flex items-center gap-1"
              >
                <ShieldCheck className="w-3 h-3 text-cyan-400" />
                {ref}
              </span>
            ))}
          </div>
        </div>

        {/* 5. GROUNDING VALIDATION AUDIT ACCORDION */}
        <div className="mt-4 pt-3 border-t border-slate-800">
          <button
            onClick={() => setShowGroundingDetails(!showGroundingDetails)}
            className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition-colors py-1"
          >
            <span className="flex items-center gap-2 font-bold text-[11px]">
              <ShieldCheck className={`w-4 h-4 ${isGroundingVerified ? 'text-emerald-400' : 'text-amber-400'}`} />
              GROUNDING VALIDATION CHECKS ({aiData.grounding_details?.passed_checks?.length || 0} PASSED, {aiData.grounding_details?.failed_checks?.length || 0} FAILED)
            </span>
            {showGroundingDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showGroundingDetails && (
            <div className="mt-3 p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] space-y-2.5">
              <div className="space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-500">Passed Deterministic Guardrails:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {aiData.grounding_details?.passed_checks?.map((check, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 text-emerald-400">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{check.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>

              {aiData.grounding_details?.failed_checks?.length > 0 && (
                <div className="pt-2 border-t border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-red-400">Failed Checks / Issues:</span>
                  {aiData.grounding_details?.issues?.map((issue, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-red-300">
                      <XCircle className="w-3.5 h-3.5 text-red-400 mt-0.5" />
                      <span>{issue}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </CyberCard>
    </div>
  );
}
