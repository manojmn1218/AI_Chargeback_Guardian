import React, { useState, useEffect } from 'react';
import {
  UserCheck,
  CheckCircle2,
  XCircle,
  Edit3,
  HelpCircle,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Send,
  FileText,
  Copy,
  Check,
  Clock,
  Sparkles,
  RefreshCw,
  Lock,
} from 'lucide-react';
import CyberCard from './CyberCard';
import { getDisputeReviewStatus, submitDisputeReview } from '../services/api';
import { cyberSound } from '../utils/cyberSound';
import { useAuth } from '../context/AuthContext';

export default function HumanReviewPanel({ disputeId, onReviewComplete }) {
  const { user } = useAuth();
  const [reviewData, setReviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Review form state
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [reviewerRef, setReviewerRef] = useState(user?.reviewer_id || 'REV-00892');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (user?.reviewer_id) {
      setReviewerRef(user.reviewer_id);
    }
  }, [user]);


  useEffect(() => {
    fetchReviewStatus();
  }, [disputeId]);

  async function fetchReviewStatus() {
    try {
      setLoading(true);
      setError(null);
      const data = await getDisputeReviewStatus(disputeId);
      setReviewData(data);
      setEditedText(data.final_response || data.original_ai_response || '');
      if (data.latest_review?.reviewer_notes) {
        setReviewerNotes(data.latest_review.reviewer_notes);
      }
    } catch (err) {
      console.error('Failed to load review status:', err);
      setError(err.response?.data?.detail || 'Failed to load review status');
    } finally {
      setLoading(false);
    }
  }

  const handleCopy = () => {
    const textToCopy = isEditing ? editedText : (reviewData?.final_response || reviewData?.original_ai_response || '');
    navigator.clipboard.writeText(textToCopy);
    cyberSound.playClick();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDecision = async (decisionType) => {
    // Validation checks
    if (decisionType === 'EDIT_AND_APPROVE' && (!editedText || editedText.trim().length < 10)) {
      setError('An edited response of at least 10 characters is required for Edit & Approve.');
      return;
    }
    if (decisionType === 'NEEDS_MORE_EVIDENCE' && (!reviewerNotes || reviewerNotes.trim().length < 5)) {
      setError('Reviewer notes explaining what evidence is missing are required when requesting more evidence.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      const payload = {
        decision: decisionType,
        reviewer_reference: reviewerRef,
        edited_response: decisionType === 'EDIT_AND_APPROVE' ? editedText : null,
        reviewer_notes: reviewerNotes || null,
      };

      const updated = await submitDisputeReview(disputeId, payload);
      cyberSound.playSuccess();
      setReviewData(updated);
      setSuccessMessage(`Decision [${decisionType}] successfully authorized and recorded in audit trail.`);
      if (onReviewComplete) {
        onReviewComplete(updated);
      }
    } catch (err) {
      console.error('Failed to submit review decision:', err);
      cyberSound.playWarning();
      setError(err.response?.data?.detail || 'Failed to submit review decision');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <CyberCard title="HUMAN-IN-THE-LOOP REVIEW GATE" icon={UserCheck} glowColor="indigo">
        <div className="flex flex-col items-center justify-center py-12 space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
          <span className="text-xs font-mono text-slate-400">Loading dispute review status...</span>
        </div>
      </CyberCard>
    );
  }

  if (!reviewData) return null;

  const {
    current_status,
    original_ai_recommendation,
    original_ai_response,
    final_response,
    grounding_status,
    can_approve,
    grounding_warning,
    latest_review,
    all_reviews = [],
  } = reviewData;

  const isGroundingPassed = grounding_status === 'VERIFIED';
  const isApproved = current_status === 'APPROVED' || current_status === 'EDITED_AND_APPROVED';

  return (
    <CyberCard title="HUMAN-IN-THE-LOOP REVIEW GATE (Step 6)" icon={UserCheck} glowColor="cyan">
      <div className="space-y-6 font-sans">
        {/* 1. Status & Safeguard Summary Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 rounded-xl bg-slate-950/70 border border-slate-800 font-mono">
          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Review State</span>
            <span
              className={`inline-block mt-1 text-xs font-bold px-2.5 py-1 rounded uppercase ${
                current_status === 'APPROVED' || current_status === 'EDITED_AND_APPROVED'
                  ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                  : current_status === 'REJECTED'
                  ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                  : current_status === 'NEEDS_MORE_EVIDENCE'
                  ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                  : 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20'
              }`}
            >
              {current_status.replace(/_/g, ' ')}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">AI Recommendation</span>
            <span className="inline-block mt-1 text-xs font-bold text-cyan-300">
              {original_ai_recommendation || 'CONTEST'}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Grounding Safeguard</span>
            <div className="flex items-center gap-1.5 mt-1">
              {isGroundingPassed ? (
                <>
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-emerald-400">PASSED</span>
                </>
              ) : (
                <>
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  <span className="text-xs font-bold text-rose-400">FAILED (BLOCKED)</span>
                </>
              )}
            </div>
          </div>

          <div>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Reviewer ID</span>
            <input
              type="text"
              value={reviewerRef}
              onChange={(e) => setReviewerRef(e.target.value)}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-0.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* 2. Grounding Safeguard Failure Banner (if blocked) */}
        {!can_approve && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs font-mono flex items-start gap-3">
            <Lock className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-white font-bold block mb-1">APPROVAL GATE LOCKED:</strong>
              {grounding_warning || 'Approval is strictly prohibited because AI grounding validation failed.'}
            </div>
          </div>
        )}

        {/* 3. Success / Error Feedback Alerts */}
        {successMessage && (
          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* 4. Response Rebuttal Draft (View / Edit Mode) */}
        <div className="space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                {isEditing ? 'EDITING REBUTTAL DRAFT' : 'AUTHORITATIVE REBUTTAL DRAFT'}
              </span>
              {latest_review?.reviewer_decision === 'EDIT_AND_APPROVED' && (
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/30">
                  Edited by human reviewer ({latest_review.reviewer_reference})
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  cyberSound.playClick();
                  setIsEditing(!isEditing);
                }}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold transition-all ${
                  isEditing
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                <Edit3 className="w-3 h-3" />
                <span>{isEditing ? 'Done Editing' : 'Edit Draft'}</span>
              </button>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          </div>

          {isEditing ? (
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              rows={14}
              placeholder="Edit dispute rebuttal response..."
              className="w-full p-4 rounded-xl bg-slate-950 border border-indigo-500/50 text-slate-200 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 leading-relaxed"
            />
          ) : (
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300 font-mono text-xs whitespace-pre-wrap max-h-80 overflow-y-auto leading-relaxed">
              {final_response || original_ai_response || 'No AI draft available.'}
            </div>
          )}
        </div>

        {/* 5. Reviewer Notes */}
        <div className="space-y-1.5 font-mono text-xs">
          <label className="text-[10px] text-slate-400 uppercase font-bold block">
            Reviewer Investigation Notes (Mandatory for 'Request More Evidence')
          </label>
          <textarea
            value={reviewerNotes}
            onChange={(e) => setReviewerNotes(e.target.value)}
            rows={3}
            placeholder="Document reasoning, evidence verification observations, or missing courier records..."
            className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-cyan-500 leading-relaxed"
          />
        </div>

        {/* 6. Human Review Decision Action Buttons */}
        <div className="pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Button 1: Approve */}
            <button
              onClick={() => {
                cyberSound.playClick();
                handleDecision('APPROVE');
              }}
              disabled={submitting || !can_approve}
              className={`flex items-center justify-center gap-2 p-3 rounded-xl font-mono text-xs font-bold transition-all ${
                !can_approve
                  ? 'bg-slate-800/40 text-slate-600 border border-slate-800 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 active:scale-95'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>APPROVE & CONTEST</span>
            </button>

            {/* Button 2: Edit & Approve */}
            <button
              onClick={() => {
                cyberSound.playClick();
                handleDecision('EDIT_AND_APPROVE');
              }}
              disabled={submitting || !can_approve}
              className={`flex items-center justify-center gap-2 p-3 rounded-xl font-mono text-xs font-bold transition-all ${
                !can_approve
                  ? 'bg-slate-800/40 text-slate-600 border border-slate-800 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 active:scale-95'
              }`}
            >
              <Edit3 className="w-4 h-4" />
              <span>EDIT & APPROVE</span>
            </button>

            {/* Button 3: Reject Claim */}
            <button
              onClick={() => {
                cyberSound.playClick();
                handleDecision('REJECT');
              }}
              disabled={submitting}
              className="flex items-center justify-center gap-2 p-3 rounded-xl bg-rose-600/80 hover:bg-rose-500 text-white font-mono text-xs font-bold shadow-lg shadow-rose-600/20 active:scale-95 transition-all"
            >
              <XCircle className="w-4 h-4" />
              <span>REJECT CLAIM</span>
            </button>

            {/* Button 4: Request More Evidence */}
            <button
              onClick={() => {
                cyberSound.playClick();
                handleDecision('NEEDS_MORE_EVIDENCE');
              }}
              disabled={submitting}
              className="flex items-center justify-center gap-2 p-3 rounded-xl bg-amber-600/80 hover:bg-amber-500 text-white font-mono text-xs font-bold shadow-lg shadow-amber-600/20 active:scale-95 transition-all"
            >
              <HelpCircle className="w-4 h-4" />
              <span>REQUEST MORE EVIDENCE</span>
            </button>
          </div>
        </div>
      </div>
    </CyberCard>
  );
}
