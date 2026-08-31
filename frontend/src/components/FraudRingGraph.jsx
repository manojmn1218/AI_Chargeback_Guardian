import React, { useState, useEffect } from 'react';
import { Network, ShieldAlert, Cpu, Layers, Loader2, Sparkles } from 'lucide-react';
import CyberCard from './CyberCard';
import { getFraudRingGraph } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

export default function FraudRingGraph() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        const res = await getFraudRingGraph();
        setData(res);
      } catch (err) {
        console.error('Failed to load fraud ring graph:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, []);

  return (
    <CyberCard className="relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            <span className="text-[10px] font-mono font-bold text-rose-400 uppercase tracking-wider">
              Entity Linking Syndicate Radar
            </span>
          </div>
          <h2 className="text-sm font-mono font-bold text-white tracking-tight flex items-center gap-2 mt-0.5">
            <Network className="w-4 h-4 text-indigo-400" />
            <span>Fraud Ring & Shared Device Network Graph</span>
          </h2>
          <p className="text-[10px] font-mono text-slate-400">
            Multi-Account Graph Clustering (Identifies shared hardware IDs, IP subnets, & credit cards)
          </p>
        </div>

        {data && (
          <div className="flex items-center gap-3 font-mono text-xs">
            <div className="px-3 py-1 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300">
              <span className="font-bold">{data.syndicates_count}</span> Syndicates Flagged
            </div>
            <div className="px-3 py-1 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
              <span className="font-bold">${data.total_flagged_amount.toLocaleString()}</span> At Risk
            </div>
          </div>
        )}
      </div>

      {/* Interactive Visual Network SVG Container */}
      <div className="h-64 sm:h-80 w-full rounded-2xl bg-slate-950/90 border border-slate-800/80 relative flex items-center justify-center overflow-hidden font-mono">
        {loading ? (
          <div className="text-center text-slate-500 text-xs">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400 mx-auto mb-2" />
            Analyzing relational entity links...
          </div>
        ) : (
          <svg className="w-full h-full">
            {/* Grid Background */}
            <defs>
              <pattern id="graphGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1" fill="#1e293b" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#graphGrid)" />

            {/* Render Links */}
            {data?.links?.map((link, idx) => {
              const srcIdx = idx % 8;
              const x1 = 120 + (srcIdx * 65);
              const y1 = 60 + ((idx % 3) * 75);
              const x2 = 380;
              const y2 = 140;
              return (
                <line
                  key={idx}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="#4f46e5"
                  strokeWidth="1.5"
                  strokeOpacity="0.4"
                  strokeDasharray="4 2"
                />
              );
            })}

            {/* Central Cluster Hub (Device) */}
            <g
              transform="translate(380, 140)"
              className="cursor-pointer"
              onClick={() => {
                cyberSound.playClick();
                setSelectedNode({
                  type: 'DEVICE',
                  label: 'DEV-SHARED-002 (MacBook Pro M2 / iOS)',
                  detail: 'Linked to 5 customer dispute cases across 3 zip codes',
                  risk: 'CRITICAL (High Velocity Abuse)',
                });
              }}
            >
              <circle r="26" fill="#ef4444" fillOpacity="0.15" stroke="#ef4444" strokeWidth="2" />
              <circle r="14" fill="#ef4444" />
              <text y="35" textAnchor="middle" fill="#fca5a5" fontSize="10" fontWeight="bold">
                Device Syndicate #01
              </text>
            </g>

            {/* Satellite Customer Nodes */}
            {data?.nodes?.filter((n) => n.type === 'customer').slice(0, 8).map((node, idx) => {
              const x = 120 + ((idx % 4) * 110);
              const y = 60 + (Math.floor(idx / 4) * 120);
              const isSelected = selectedNode?.label === node.label;
              return (
                <g
                  key={node.id}
                  transform={`translate(${x}, ${y})`}
                  className="cursor-pointer group"
                  onClick={() => {
                    cyberSound.playClick();
                    setSelectedNode({
                      type: 'CUSTOMER',
                      label: node.label,
                      detail: 'Purchased electronics within 2 hours of account creation',
                      risk: 'SUSPECTED_FRIENDLY_FRAUD',
                    });
                  }}
                >
                  <circle
                    r="16"
                    fill={isSelected ? '#06b6d4' : '#6366f1'}
                    fillOpacity="0.2"
                    stroke={isSelected ? '#22d3ee' : '#818cf8'}
                    strokeWidth="1.5"
                  />
                  <circle r="8" fill={isSelected ? '#06b6d4' : '#6366f1'} />
                  <text y="24" textAnchor="middle" fill="#cbd5e1" fontSize="9">
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        )}

        {/* Selected Node Details Overlay */}
        {selectedNode && (
          <div className="absolute bottom-3 left-3 right-3 sm:right-auto sm:max-w-md p-3 rounded-xl bg-slate-900/95 border border-indigo-500/40 shadow-2xl backdrop-blur-xl animate-fade-in text-[10px]">
            <div className="flex items-center justify-between font-bold text-white mb-1">
              <span className="text-cyan-400">{selectedNode.label}</span>
              <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                {selectedNode.risk}
              </span>
            </div>
            <p className="text-slate-300">{selectedNode.detail}</p>
          </div>
        )}
      </div>
    </CyberCard>
  );
}
