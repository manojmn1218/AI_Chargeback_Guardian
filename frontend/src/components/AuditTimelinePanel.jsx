import React, { useState, useEffect } from 'react';
import {
  History,
  Shield,
  Bot,
  User,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import CyberCard from './CyberCard';
import { getDisputeAuditTrail } from '../services/api';

export default function AuditTimelinePanel({ disputeId }) {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchAuditTrail();
  }, [disputeId]);

  async function fetchAuditTrail() {
    try {
      setLoading(true);
      setError(null);
      const data = await getDisputeAuditTrail(disputeId);
      setAuditData(data);
    } catch (err) {
      console.error('Failed to load audit trail:', err);
      setError(err.response?.data?.detail || 'Failed to load investigation audit history');
    } finally {
      setLoading(false);
    }
  }

  const getActorBadge = (actorType) => {
    switch (actorType) {
      case 'HUMAN':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
            <User className="w-3 h-3 text-emerald-400" /> HUMAN
          </span>
        );
      case 'AI':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold">
            <Bot className="w-3 h-3 text-cyan-400" /> AI AGENT
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-bold">
            <Shield className="w-3 h-3 text-slate-400" /> SYSTEM
          </span>
        );
    }
  };

  if (loading) {
    return (
      <CyberCard title="INVESTIGATION AUDIT HISTORY" icon={History} glowColor="indigo">
        <div className="flex flex-col items-center justify-center py-12 space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
          <span className="text-xs font-mono text-slate-400">Loading immutable audit logs...</span>
        </div>
      </CyberCard>
    );
  }

  if (error) {
    return (
      <CyberCard title="INVESTIGATION AUDIT HISTORY" icon={History} glowColor="rose">
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-xs font-mono">
          {error}
        </div>
      </CyberCard>
    );
  }

  if (!auditData) return null;

  const { events = [] } = auditData;

  return (
    <CyberCard title="INVESTIGATION AUDIT HISTORY & TIMELINE" icon={History} glowColor="indigo">
      <div className="space-y-4 font-sans">
        <div className="flex items-center justify-between font-mono text-xs text-slate-400 pb-2 border-b border-slate-800">
          <span>Total Immutable Events: <strong className="text-white">{events.length}</strong></span>
          <span className="text-[10px] text-slate-500">Sorted Chronologically</span>
        </div>

        {events.length === 0 ? (
          <div className="text-xs font-mono text-slate-500 py-6 text-center">No audit records found.</div>
        ) : (
          <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {events.map((ev, idx) => {
              const isExpanded = expandedId === ev.id;
              const hasMetadata = ev.metadata && Object.keys(ev.metadata).length > 0;

              return (
                <div key={ev.id || idx} className="relative group">
                  {/* Node Icon */}
                  <div className="absolute -left-6 top-1.5 w-3 h-3 rounded-full bg-slate-900 border-2 border-indigo-500 group-hover:border-cyan-400 transition-colors" />

                  <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 transition-all font-mono space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white tracking-wide">
                          {ev.action.replace(/_/g, ' ')}
                        </span>
                        {getActorBadge(ev.actor_type)}
                      </div>

                      <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>{ev.timestamp_formatted}</span>
                      </div>
                    </div>

                    {hasMetadata && (
                      <div className="pt-1">
                        <button
                          onClick={() => setExpandedId(isExpanded ? null : ev.id)}
                          className="flex items-center gap-1 text-[10px] text-indigo-400 hover:text-indigo-300 transition-colors"
                        >
                          <span>{isExpanded ? 'Hide Metadata' : 'View Event Metadata'}</span>
                          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>

                        {isExpanded && (
                          <pre className="mt-2 p-2.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-cyan-300/90 overflow-x-auto whitespace-pre-wrap">
                            {JSON.stringify(ev.metadata, null, 2)}
                          </pre>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </CyberCard>
  );
}
