import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  XCircle,
  FileText,
  Shield,
  Layers,
  ExternalLink,
  Eye,
  X,
  Info,
} from 'lucide-react';
import { cyberSound } from '../utils/cyberSound';

export default function EvidenceChecklist({ items = [], onInspectItem }) {
  const [selectedItem, setSelectedItem] = useState(null);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'AVAILABLE_VERIFIED':
        return (
          <span className="flex items-center gap-1 font-mono text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
            <CheckCircle2 className="w-3 h-3" /> VERIFIED
          </span>
        );
      case 'AVAILABLE_UNVERIFIED':
        return (
          <span className="flex items-center gap-1 font-mono text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/25">
            <AlertCircle className="w-3 h-3" /> UNVERIFIED
          </span>
        );
      case 'MISSING':
      default:
        return (
          <span className="flex items-center gap-1 font-mono text-[10px] font-bold px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 border border-red-500/25">
            <XCircle className="w-3 h-3" /> MISSING
          </span>
        );
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-300 font-mono flex items-center gap-2">
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          7-CATEGORY EVIDENCE CHECKLIST
        </h3>
        <span className="text-[10px] font-mono text-slate-500">
          Deterministic Relational Retrieval
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
        {items.map((item, idx) => {
          const isMissing = item.status === 'MISSING';
          const isVerified = item.status === 'AVAILABLE_VERIFIED';

          return (
            <div
              key={item.evidence_type || idx}
              className={`p-3.5 rounded-xl border transition-all flex flex-col justify-between ${
                isMissing
                  ? 'bg-red-950/10 border-red-900/30'
                  : isVerified
                  ? 'bg-slate-900/60 border-slate-800 hover:border-indigo-500/40'
                  : 'bg-amber-950/10 border-amber-900/30'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold text-slate-200">
                    {item.category_display_name || item.evidence_type}
                  </span>
                  {getStatusBadge(item.status)}
                </div>

                <p className="text-slate-400 text-[11px] leading-relaxed mb-3">
                  {item.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                <span className="text-slate-500 truncate max-w-[170px]" title={item.source_reference}>
                  Src: {item.source_reference || 'N/A'}
                </span>

                <button
                  onClick={() => {
                    cyberSound.playClick();
                    setSelectedItem(item);
                  }}
                  className="flex items-center gap-1 text-indigo-400 hover:text-cyan-300 transition-colors font-bold"
                >
                  <Eye className="w-3 h-3" />
                  <span>Inspect</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Raw Item Inspection Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div
            className="w-full max-w-lg rounded-2xl p-6 relative font-mono text-xs space-y-4"
            style={{
              background: 'linear-gradient(135deg, rgba(15, 20, 45, 0.95) 0%, rgba(9, 13, 30, 0.98) 100%)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7)',
            }}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-cyan-400" />
                <h4 className="text-sm font-bold text-white">
                  {selectedItem.category_display_name}
                </h4>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-500">CATEGORY TYPE</span>
                <span className="text-indigo-400 font-bold">{selectedItem.evidence_type}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-500">VERIFICATION STATUS</span>
                <span>{getStatusBadge(selectedItem.status)}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-500">SOURCE REFERENCE</span>
                <span className="text-cyan-400">{selectedItem.source_reference}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-500">RECORD TIMESTAMP</span>
                <span className="text-slate-300">
                  {selectedItem.evidence_timestamp
                    ? new Date(selectedItem.evidence_timestamp).toUTCString()
                    : 'Not Available'}
                </span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-500">DISPUTE RELEVANCE</span>
                <span className="text-emerald-400 font-bold">
                  {Math.round((selectedItem.relevance_score || 0.5) * 100)}%
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                <p className="text-[10px] text-slate-500 uppercase font-bold">Record Description</p>
                <p className="text-slate-300 text-xs leading-relaxed">{selectedItem.description}</p>
              </div>

              {selectedItem.strength_rationale && (
                <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 space-y-1">
                  <p className="text-[10px] text-indigo-400 uppercase font-bold">Investigation Rationale</p>
                  <p className="text-slate-300 text-xs">{selectedItem.strength_rationale}</p>
                </div>
              )}
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold transition-colors text-xs"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
