import React from 'react';
import {
  CreditCard,
  ShoppingCart,
  Truck,
  PackageCheck,
  RotateCcw,
  MessageSquare,
  AlertTriangle,
  Clock,
  ShieldAlert,
  CheckCircle2,
  Calendar,
} from 'lucide-react';

export default function InvestigationTimeline({ events = [] }) {
  const getEventIcon = (type) => {
    switch (type) {
      case 'TRANSACTION':
        return <CreditCard className="w-3.5 h-3.5 text-cyan-400" />;
      case 'ORDER':
        return <ShoppingCart className="w-3.5 h-3.5 text-indigo-400" />;
      case 'SHIPMENT':
        return <Truck className="w-3.5 h-3.5 text-amber-400" />;
      case 'DELIVERY':
        return <PackageCheck className="w-3.5 h-3.5 text-emerald-400" />;
      case 'REFUND':
        return <RotateCcw className="w-3.5 h-3.5 text-purple-400" />;
      case 'COMMUNICATION':
        return <MessageSquare className="w-3.5 h-3.5 text-blue-400" />;
      case 'DISPUTE':
      default:
        return <ShieldAlert className="w-3.5 h-3.5 text-red-400" />;
    }
  };

  const getStatusBadgeStyle = (status) => {
    switch (status) {
      case 'AUTHORIZED':
      case 'FULFILLED':
      case 'DELIVERED':
      case 'PROCESSED':
      case 'VERIFIED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25';
      case 'SHIPPED':
      case 'UNDER_REVIEW':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/25';
      case 'UNVERIFIED':
      case 'UNCONFIRMED':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/25';
      case 'MISSING_TIMESTAMP':
      case 'OPEN':
        return 'bg-red-500/10 text-red-400 border-red-500/25';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-300 flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          CHRONOLOGICAL INVESTIGATION TIMELINE
        </h3>
        <span className="text-[10px] text-slate-500">
          {events.length} Milestones Tracked
        </span>
      </div>

      {events.length === 0 ? (
        <div className="p-6 text-center text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
          No chronological timeline events found.
        </div>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-cyan-500 before:via-indigo-500 before:to-red-500/40">
          {events.map((evt, idx) => {
            const isMissingTimestamp = !evt.is_available || !evt.timestamp;

            return (
              <div key={evt.event_id || idx} className="relative group">
                {/* Milestone Node */}
                <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-slate-950 border border-slate-700 flex items-center justify-center shadow-md group-hover:border-cyan-400 transition-colors">
                  {getEventIcon(evt.event_type)}
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 hover:border-slate-700 transition-all space-y-1.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-200 text-xs">
                        {evt.title}
                      </span>
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${getStatusBadgeStyle(
                          evt.status_badge
                        )}`}
                      >
                        {evt.status_badge}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-[11px] text-slate-400">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      <span>
                        {isMissingTimestamp ? (
                          <span className="text-amber-400 font-bold">MISSING TIMESTAMP</span>
                        ) : (
                          evt.timestamp_formatted || new Date(evt.timestamp).toLocaleString()
                        )}
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-400 text-[11px] leading-relaxed">
                    {evt.description}
                  </p>

                  <div className="text-[10px] text-slate-500 flex items-center gap-2 pt-1 border-t border-slate-800/40">
                    <span>Source: <strong className="text-slate-400">{evt.source}</strong></span>
                    <span>·</span>
                    <span>ID: {evt.event_id}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
