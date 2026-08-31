import React, { useState } from 'react';
import { Sparkles, Send, Loader2, Check, RefreshCw, X, MessageSquare } from 'lucide-react';
import { refineRebuttal } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

const QUICK_PROMPTS = [
  { label: '👔 Formal Legal Scheme Tone', prompt: 'Make the tone formal legal and cite card scheme arbitration rules' },
  { label: '📦 Emphasize Courier GPS & POD', prompt: 'Emphasize FedEx physical GPS delivery and signed proof of delivery' },
  { label: '⏱️ Enforce 14-Day Return Policy', prompt: 'Highlight the merchant 14-day cancellation and return policy terms' },
  { label: '✂️ Concise 3-Point Summary', prompt: 'Summarize into a concise 3-bullet rebuttal for rapid bank processing' },
];

export default function AIChatRefinerModal({ disputeId, currentDraft, onApplied, onClose }) {
  const [promptText, setPromptText] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewText, setPreviewText] = useState('');
  const [error, setError] = useState(null);

  const handleRefine = async (instruction) => {
    const textToUse = instruction || promptText;
    if (!textToUse.trim()) return;
    try {
      setLoading(true);
      setError(null);
      cyberSound.playClick();
      const res = await refineRebuttal(disputeId, textToUse, currentDraft);
      setPreviewText(res.refined_rebuttal);
      cyberSound.playSuccess();
    } catch (err) {
      console.error('Refinement failed:', err);
      setError('Refinement failed: ' + (err.response?.data?.detail || err.message));
      cyberSound.playError();
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (previewText) {
      onApplied(previewText);
      cyberSound.playSuccess();
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="w-full max-w-2xl rounded-3xl p-6 border shadow-2xl relative font-mono text-xs overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(9, 13, 30, 0.99) 100%)',
          borderColor: 'rgba(99, 102, 241, 0.4)',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.15)',
        }}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Interactive AI Rebuttal Copilot</h3>
              <p className="text-[10px] text-slate-400">Custom prompt guidance with zero hallucinated citations</p>
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

        {/* Quick Prompt Pills */}
        <div className="mt-4">
          <label className="text-[10px] text-slate-400 uppercase font-bold block mb-1.5">
            1-Click Prompt Directives
          </label>
          <div className="flex flex-wrap gap-2">
            {QUICK_PROMPTS.map((qp, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setPromptText(qp.prompt);
                  handleRefine(qp.prompt);
                }}
                className="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-indigo-600/10 text-slate-300 hover:text-indigo-300 text-[10px] transition-all cursor-pointer"
              >
                {qp.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom Input */}
        <div className="mt-4 flex items-center gap-2">
          <input
            type="text"
            placeholder="e.g. 'Emphasize that the customer signed upon delivery and accepted terms...'"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRefine()}
            className="flex-1 px-3.5 py-2 rounded-xl bg-slate-950/90 border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            type="button"
            disabled={loading || !promptText.trim()}
            onClick={() => handleRefine()}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            <span>Refine</span>
          </button>
        </div>

        {error && <p className="text-[11px] text-rose-400 mt-2">{error}</p>}

        {/* Preview Area */}
        <div className="mt-4">
          <label className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
            Grounded Rebuttal Preview
          </label>
          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 h-44 overflow-y-auto text-[11px] text-slate-300 font-mono whitespace-pre-wrap">
            {previewText || currentDraft || 'Click a directive above or enter a prompt to generate refined text...'}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Deterministic Citation Validator Active</span>
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
              disabled={!previewText}
              onClick={handleApply}
              className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Apply to Review Form</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
