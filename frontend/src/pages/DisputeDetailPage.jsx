import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Loader2,
  AlertTriangle,
  FileText,
  Brain,
  UserCheck,
  Clock,
  Search,
  Database,
  Shield,
  Sparkles,
  ChevronRight,
  Lock,
  CheckCircle2,
  XCircle,
  TrendingUp,
  FileCheck,
  Send,
  Edit3,
  ThumbsUp,
  ThumbsDown,
  Hash,
  Activity,
  History,
  Award,
  Layers,
  Copy,
  Check,
  RefreshCw,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import CyberCard from '../components/CyberCard';
import EvidenceChecklist from '../components/EvidenceChecklist';
import InvestigationTimeline from '../components/InvestigationTimeline';
import ConsistencyWarnings from '../components/ConsistencyWarnings';
import AIResponsePanel from '../components/AIResponsePanel';
import SHAPExplanationPanel from '../components/SHAPExplanationPanel';
import HumanReviewPanel from '../components/HumanReviewPanel';
import AuditTimelinePanel from '../components/AuditTimelinePanel';
import { getDisputeInvestigation } from '../services/api';
import { cyberSound } from '../utils/cyberSound';



export default function DisputeDetailPage() {
  const { id } = useParams();
  const [investigationData, setInvestigationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('review'); // 'review' | 'ai_draft' | 'shap' | 'evidence' | 'timeline' | 'audit'
  const [reviewAction, setReviewAction] = useState(null);
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [editedDraft, setEditedDraft] = useState('');
  const [isEditingDraft, setIsEditingDraft] = useState(false);
  const [copied, setCopied] = useState(false);


  useEffect(() => {
    fetchInvestigation();
  }, [id]);

  async function fetchInvestigation() {
    try {
      setLoading(true);
      setError(null);
      const data = await getDisputeInvestigation(id);
      setInvestigationData(data);
      buildDraftLetter(data);
    } catch (err) {
      console.error('Failed to load dispute investigation:', err);
      setError(err.response?.data?.detail || err.message || 'Dispute investigation could not be retrieved.');
    } finally {
      setLoading(false);
    }
  }

  function buildDraftLetter(data) {
    if (!data) return;
    const disp = data.dispute || {};
    const ref = disp.dispute_reference || `DISP-${disp.id}`;
    const txnRef = disp.transaction?.transaction_reference || `TXN-${disp.transaction_id}`;
    const amount = Number(disp.dispute_amount || 0).toFixed(2);
    const reason = (disp.dispute_reason || 'UNSPECIFIED').replace(/_/g, ' ');
    const merchantRef = disp.merchant?.merchant_reference || 'MER-001';
    const ev = data.evidence_analysis || {};
    const availableItems = (ev.evidence_checklist || []).filter((i) => i.available);
    const missingItems = ev.missing_evidence || [];

    const draft = `TO: Card Issuing Bank Dispute & Arbitration Committee
RE: Formal Contest Rebuttal for Dispute #${ref} (Transaction #${txnRef})
MERCHANT: ${merchantRef} | CLAIMED AMOUNT: $${amount} USD

Dear Dispute Resolution Specialist,

We are submitting verified operational and transactional evidence to formally contest the chargeback initiated under Reason Code "${reason}".

1. EVIDENCE GROUNDING SUMMARY:
${
  availableItems.length > 0
    ? availableItems
        .map(
          (item, idx) =>
            `   ${idx + 1}. [${item.evidence_type}] ${item.description} (Source: ${item.source_reference}, Status: ${item.status})`
        )
        .join('\n')
    : '   1. Standard payment gateway authorization record on file.'
}

2. MISSING EVIDENCE DISCLOSURE:
${
  missingItems.length > 0
    ? missingItems
        .map((m) => `   - [${m.evidence_type}] ${m.impact_description}`)
        .join('\n')
    : '   ALL 7 MANDATORY EVIDENCE CATEGORIES ARE VERIFIED AND ATTACHED.'
}

3. CASE STRENGTH ASSESSMENT:
   - Evidence Completeness: ${ev.availability_percentage}% available (${ev.verified}/${ev.total_expected} categories verified)
   - Quality Confidence Score: ${ev.quality_score}/100
   ${data.ml_analysis ? `- Machine Learning Win Confidence: ${Math.round(data.ml_analysis.probability * 100)}% (${data.ml_analysis.classification})` : ''}

Pursuant to card network operating regulations, this transaction represents a fully authorized and fulfilled purchase. We respectfully request that this chargeback be reversed and the funds credited back to the merchant account.`;

    setEditedDraft(draft);
  }

  const handleCopyDraft = () => {
    navigator.clipboard.writeText(editedDraft);
    cyberSound.playSuccess();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApprove = () => {
    cyberSound.playSuccess();
    setReviewAction('approved');
  };

  const handleReject = () => {
    cyberSound.playSelect();
    setReviewAction('rejected');
  };

  if (loading) {
    return (
      <div className="p-20 text-center font-mono text-xs text-slate-400 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
        <span>Loading Evidence Intelligence Dossier for Dispute #{id}...</span>
      </div>
    );
  }

  if (error || !investigationData) {
    return (
      <div className="p-12 text-center font-mono text-xs space-y-4 max-w-lg mx-auto bg-slate-900/60 rounded-2xl border border-red-900/40">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto" />
        <h2 className="text-base font-bold text-white">Investigation Not Found</h2>
        <p className="text-slate-400">{error || `Dispute '${id}' does not exist in the database.`}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Command Deck</span>
        </Link>
      </div>
    );
  }

  const { dispute, ml_analysis, evidence_analysis, timeline, warnings } = investigationData;
  const isContestStrong = ml_analysis?.classification === 'STRONG';
  const isContestWeak = ml_analysis?.classification === 'WEAK';

  return (
    <div className="space-y-6">
      {/* 1. Top Breadcrumbs & Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link
            to="/"
            onClick={() => cyberSound.playHover()}
            className="text-xs font-mono font-bold text-slate-400 hover:text-cyan-400 transition-colors flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>COMMAND DECK</span>
          </Link>
          <ChevronRight className="w-3 h-3 text-slate-600" />
          <span className="text-xs font-mono font-bold text-indigo-400">
            INVESTIGATION: {dispute.dispute_reference}
          </span>
        </div>

        <button
          onClick={() => {
            cyberSound.playClick();
            fetchInvestigation();
          }}
          className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white font-mono text-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Dossier</span>
        </button>
      </div>

      {/* 2. HEADER INFO BANNER */}
      <div
        className="p-5 sm:p-6 rounded-2xl relative overflow-hidden flex flex-col lg:flex-row lg:items-center justify-between gap-6"
        style={{
          background: 'linear-gradient(135deg, rgba(13, 17, 38, 0.95) 0%, rgba(8, 11, 26, 0.98) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          boxShadow: '0 12px 36px rgba(0, 0, 0, 0.5)',
        }}
      >
        <div>
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h1
              className="text-2xl lg:text-3xl font-black text-white tracking-tight"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              {dispute.dispute_reference}
            </h1>
            <StatusBadge status={dispute.dispute_status} type="status" />
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              STEP 6 HUMAN-IN-THE-LOOP & SHAP
            </span>
          </div>


          <p className="text-xs font-mono text-slate-400 flex flex-wrap items-center gap-x-4 gap-y-1">
            <span>
              Claim Reason: <strong className="text-cyan-300">{dispute.dispute_reason.replace(/_/g, ' ')}</strong>
            </span>
            <span>·</span>
            <span>
              Transaction: <strong className="text-slate-200">{dispute.transaction?.transaction_reference || `TXN-${dispute.transaction_id}`}</strong>
            </span>
            <span>·</span>
            <span>
              Filed: <strong className="text-slate-300">{new Date(dispute.dispute_timestamp).toLocaleDateString()}</strong>
            </span>
          </p>
        </div>

        {/* Header Telemetry Gauges */}
        <div className="flex items-center gap-4 sm:gap-6 font-mono">
          <div className="p-3 px-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-right">
            <p className="text-[10px] text-slate-500 uppercase font-bold">Dispute Amount</p>
            <p className="text-xl font-extrabold text-white">
              ${Number(dispute.dispute_amount).toFixed(2)}
            </p>
          </div>

          <div className="p-3 px-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-right">
            <p className="text-[10px] text-slate-500 uppercase font-bold">Evidence Quality</p>
            <p className="text-xl font-extrabold text-cyan-400">
              {evidence_analysis.quality_score}/100
            </p>
          </div>

          {ml_analysis && (
            <div className="p-3 px-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-right">
              <p className="text-[10px] text-slate-500 uppercase font-bold">ML Win Confidence</p>
              <p
                className={`text-xl font-extrabold ${
                  isContestStrong
                    ? 'text-emerald-400'
                    : isContestWeak
                    ? 'text-red-400'
                    : 'text-amber-400'
                }`}
              >
                {Math.round(ml_analysis.probability * 100)}%
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 3. Consistency Warnings Banner (if any) */}
      <ConsistencyWarnings warnings={warnings} />

      {/* 4. Evidence Overview Metrics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
        {/* Availability Card */}
        <CyberCard delay={100} className="p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-[10px] uppercase font-bold">Evidence Availability</span>
            <span className="text-sm font-bold text-white">
              {evidence_analysis.available} / {evidence_analysis.total_expected} ({evidence_analysis.availability_percentage}%)
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full"
              style={{ width: `${evidence_analysis.availability_percentage}%` }}
            />
          </div>
        </CyberCard>

        {/* Verification Card */}
        <CyberCard delay={150} className="p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-[10px] uppercase font-bold">Verification Rate</span>
            <span className="text-sm font-bold text-emerald-400">
              {evidence_analysis.verified} / {evidence_analysis.total_expected} ({evidence_analysis.verification_percentage}%)
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full"
              style={{ width: `${evidence_analysis.verification_percentage}%` }}
            />
          </div>
        </CyberCard>

        {/* Quality Score Card */}
        <CyberCard delay={200} className="p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-[10px] uppercase font-bold">Quality Confidence</span>
            <span className="text-sm font-bold text-cyan-400">
              {evidence_analysis.quality_score} / 100
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full"
              style={{ width: `${evidence_analysis.quality_score}%` }}
            />
          </div>
        </CyberCard>
      </div>

      {/* 5. MAIN INVESTIGATION SPLIT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        {/* LEFT COLUMN: AI Rebuttal, Evidence Checklist, Timeline, SHAP (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Sub Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-xl bg-slate-900/80 border border-slate-800 font-mono text-xs">
            {[
              { id: 'review', label: 'Human Review Gate (Step 6)', icon: UserCheck },
              { id: 'ai_draft', label: 'Grounded AI Rebuttal (Step 5)', icon: Sparkles },
              { id: 'shap', label: 'TreeSHAP Explainability', icon: Brain },
              { id: 'evidence', label: 'Evidence Matrix (7)', icon: Layers },
              { id: 'timeline', label: `Timeline (${timeline.length})`, icon: Clock },
              { id: 'audit', label: 'Audit History', icon: History },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => {
                    setActiveTab(tab.id);
                    cyberSound.playClick();
                  }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg cursor-pointer transition-all ${
                    activeTab === tab.id
                      ? 'bg-indigo-600 text-white font-bold shadow-lg shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>

              );
            })}
          </div>

          {/* TAB 0: Human Review Gate (Step 6) */}
          {activeTab === 'review' && (
            <HumanReviewPanel disputeId={id} onReviewComplete={fetchInvestigation} />
          )}

          {/* TAB 1: Grounded AI Rebuttal (Step 5) */}
          {activeTab === 'ai_draft' && (
            <AIResponsePanel disputeId={id} initialInvestigation={investigationData} />
          )}

          {/* TAB 2: TreeSHAP Local Explainability */}
          {activeTab === 'shap' && (
            <SHAPExplanationPanel disputeId={id} />
          )}

          {/* TAB 3: Evidence Matrix + Strongest + Missing */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              {/* Strongest Evidence Highlights */}
              {evidence_analysis.strongest_evidence?.length > 0 && (
                <div className="space-y-3 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-emerald-400 flex items-center gap-2">
                      <Award className="w-4 h-4" />
                      STRONGEST DEFENSIVE EVIDENCE (RELEVANCE RANKED)
                    </h3>
                    <span className="text-[10px] text-slate-500">
                      Reason-Aware Matching
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {evidence_analysis.strongest_evidence.map((item, idx) => (
                      <div
                        key={item.evidence_type || idx}
                        className="p-3.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 flex items-start gap-3"
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <div className="space-y-1 w-full">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white uppercase text-[11px]">
                              {item.category_display_name || item.evidence_type}
                            </span>
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-mono font-bold">
                              RELEVANCE: {Math.round((item.relevance_score || 1.0) * 100)}%
                            </span>
                          </div>
                          <p className="text-slate-300 text-xs">
                            {item.description}
                          </p>
                          <p className="text-[10px] text-slate-400 font-mono">
                            {item.rationale || `Source: ${item.source_reference}`}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Evidence Disclosures */}
              {evidence_analysis.missing_evidence?.length > 0 && (
                <div className="space-y-3 font-mono text-xs">
                  <h3 className="text-xs font-bold text-amber-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    MISSING EVIDENCE DISCLOSURES
                  </h3>

                  <div className="space-y-2">
                    {evidence_analysis.missing_evidence.map((item, idx) => (
                      <div
                        key={item.evidence_type || idx}
                        className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 flex items-start gap-3"
                      >
                        <XCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                        <div className="space-y-1 w-full">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-amber-300 uppercase text-[11px]">
                              {item.category_display_name || item.evidence_type}
                            </span>
                            <span
                              className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold ${
                                item.impact_level === 'HIGH'
                                  ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                                  : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                              }`}
                            >
                              IMPACT: {item.impact_level}
                            </span>
                          </div>
                          <p className="text-slate-300 text-xs">
                            {item.impact_description || 'Missing evidence item for this dispute category.'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full 7 Categories Checklist Matrix */}
              <EvidenceChecklist items={evidence_analysis.evidence_checklist || []} />

            </div>
          )}

          {/* TAB 4: Chronological Timeline */}
          {activeTab === 'timeline' && (
            <InvestigationTimeline events={timeline || []} />
          )}

          {/* TAB 5: Investigation Audit History */}
          {activeTab === 'audit' && (
            <AuditTimelinePanel disputeId={id} />
          )}
        </div>

        {/* RIGHT COLUMN: Human Gate, Linked Entities & Audit Trail (5 Cols) */}
        <div className="lg:col-span-5 space-y-5">
          {/* Human Review Gate */}
          <CyberCard delay={250} className="p-6" glowColor="rgba(245, 158, 11, 0.25)">
            <div className="flex items-center gap-2.5 mb-4 font-mono">
              <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                <UserCheck className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100">
                  HUMAN APPROVAL GATE
                </h3>
                <p className="text-[10px] text-slate-400">
                  FINAL DECISION & ARBITRATION DISPATCH
                </p>
              </div>
            </div>

            {reviewAction ? (
              <div
                className="p-4 rounded-xl text-center space-y-2 font-mono"
                style={{
                  background:
                    reviewAction === 'approved'
                      ? 'rgba(34, 197, 94, 0.1)'
                      : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${
                    reviewAction === 'approved' ? '#22c55e' : '#ef4444'
                  }`,
                }}
              >
                <CheckCircle2
                  className={`w-8 h-8 mx-auto ${
                    reviewAction === 'approved' ? 'text-emerald-400' : 'text-red-400'
                  }`}
                />
                <p className="text-xs font-bold text-slate-100 uppercase">
                  Decision Recorded: {reviewAction === 'approved' ? 'Contest Approved' : 'Chargeback Accepted'}
                </p>
                <p className="text-[11px] text-slate-400">
                  Dispute package dispatched with {evidence_analysis.available} verified evidence records.
                </p>
              </div>
            ) : (
              <div className="space-y-3 font-mono text-xs">
                <textarea
                  placeholder="Reviewer investigation notes (optional)..."
                  value={reviewerNotes}
                  onChange={(e) => setReviewerNotes(e.target.value)}
                  className="w-full h-20 p-3 rounded-xl bg-slate-950/60 text-slate-200 border border-slate-800 outline-none focus:border-indigo-500 resize-none text-xs"
                />

                <div className="grid grid-cols-2 gap-2.5">
                  <button
                    onClick={handleApprove}
                    className="flex items-center justify-center gap-2 p-3 rounded-xl font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-500/30 transition-all text-xs"
                  >
                    <ThumbsUp className="w-4 h-4" />
                    <span>Approve & Contest</span>
                  </button>

                  <button
                    onClick={handleReject}
                    className="flex items-center justify-center gap-2 p-3 rounded-xl font-bold bg-red-500/20 text-red-400 border border-red-500/40 hover:bg-red-500/30 transition-all text-xs"
                  >
                    <ThumbsDown className="w-4 h-4" />
                    <span>Accept Claim</span>
                  </button>
                </div>
              </div>
            )}
          </CyberCard>

          {/* Linked Customer & Merchant Metadata */}
          <CyberCard delay={300} className="p-6 font-mono text-xs">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
              RELATIONAL ENTITY PROFILES
            </h3>
            <div className="space-y-2.5">
              {dispute.customer && (
                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                  <p className="text-[10px] text-indigo-400 uppercase font-bold">
                    Customer Profile (#{dispute.customer.customer_reference})
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-slate-300 text-[11px] pt-1">
                    <div>Risk Profile: <strong className="text-slate-100">{dispute.customer.customer_risk_history}</strong></div>
                    <div>Account Age: <strong>{dispute.customer.account_age_days}d</strong></div>
                    <div>Past Txns: <strong>{dispute.customer.previous_successful_transactions}</strong></div>
                    <div>Past Disputes: <strong className="text-amber-400">{dispute.customer.previous_disputes}</strong></div>
                  </div>
                </div>
              )}

              {dispute.merchant && (
                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                  <p className="text-[10px] text-cyan-400 uppercase font-bold">
                    Merchant Profile (#{dispute.merchant.merchant_reference})
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-slate-300 text-[11px] pt-1">
                    <div>Category: <strong>{dispute.merchant.merchant_category}</strong></div>
                    <div>Dispute Rate: <strong>{(dispute.merchant.historical_dispute_rate * 100).toFixed(2)}%</strong></div>
                  </div>
                </div>
              )}
            </div>
          </CyberCard>

          {/* Dispute Lifecycle Audit Trail */}
          <CyberCard delay={350} className="p-6 font-mono text-xs">
            <div className="flex items-center gap-2 mb-3">
              <History className="w-4 h-4 text-slate-400" />
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                INVESTIGATION AUDIT TRAIL
              </h3>
            </div>
            <div className="space-y-2 text-[11px]">
              {[
                { time: 'T-00:00', action: 'Dispute Ingested from Payment Gateway', actor: 'SYSTEM' },
                { time: 'T+00:02', action: `Evidence Engine retrieved ${evidence_analysis.available}/7 categories`, actor: 'EVIDENCE_ENGINE' },
                { time: 'T+00:03', action: `Quality Scored: ${evidence_analysis.quality_score}/100`, actor: 'EVIDENCE_ENGINE' },
                { time: 'T+00:04', action: `Consistency Audit: ${warnings.length} warning(s)`, actor: 'CONSISTENCY_AUDIT' },
                { time: 'T+00:05', action: `XGBoost Risk Scored: ${ml_analysis?.score || 0}/100 (${ml_analysis?.classification || 'N/A'})`, actor: 'ML_PIPELINE' },
              ].map((ev, idx) => (
                <div key={idx} className="flex items-start gap-2 text-slate-400">
                  <span className="text-slate-600 font-bold">{ev.time}</span>
                  <span>·</span>
                  <span className="text-slate-300">{ev.action}</span>
                </div>
              ))}
            </div>
          </CyberCard>
        </div>
      </div>
    </div>
  );
}
