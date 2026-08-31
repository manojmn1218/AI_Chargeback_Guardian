import CyberCard from './CyberCard';
import { TrendingUp } from 'lucide-react';

/**
 * StatCard — Perfectly Aligned Bento Metric Component.
 * Features:
 * - Equal height & baseline alignment across all cards in a grid row
 * - Vertically centered header with icon, title, and trend badge
 * - Crisp number rendering
 * - Consistent footer spacing
 */
export default function StatCard({
  title,
  value,
  icon: Icon,
  color = '#818cf8',
  bgColor,
  subtitle,
  glowColor = 'rgba(99, 102, 241, 0.15)',
  delay = 0,
  span = 1,
  trend,
  trendPositive = true,
}) {
  return (
    <CyberCard
      delay={delay}
      glowColor={glowColor}
      accentColor={color}
      className={`p-5 h-full ${span === 2 ? 'col-span-2' : ''}`}
    >
      {/* Top Header Row: Icon + Title (Left) and Trend Badge (Right) */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          {Icon && (
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-105"
              style={{
                background: bgColor || 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.08))',
                border: `1px solid ${color}30`,
              }}
            >
              <Icon className="w-4 h-4" style={{ color }} strokeWidth={2.2} />
            </div>
          )}
          <span
            className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 truncate"
          >
            {title}
          </span>
        </div>

        {/* Trend / Status Tag */}
        {trend && (
          <div
            className="flex items-center gap-1 px-2 py-0.5 rounded-full font-mono text-[9px] font-bold flex-shrink-0"
            style={{
              background: trendPositive ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)',
              color: trendPositive ? '#4ade80' : '#f87171',
              border: `1px solid ${trendPositive ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
            }}
          >
            <TrendingUp className="w-2.5 h-2.5" />
            <span>{trend}</span>
          </div>
        )}
      </div>

      {/* Main Metric Value */}
      <div className="my-1">
        <span
          className="text-3xl lg:text-4xl font-black tracking-tight text-white block leading-none"
          style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            textShadow: `0 0 24px ${glowColor}`,
          }}
        >
          {value}
        </span>
      </div>

      {/* Footer Subtitle with guaranteed minimum height for grid alignment */}
      <div className="mt-2 min-h-[18px] flex items-center gap-1.5">
        {subtitle ? (
          <>
            <div className="w-1 h-1 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
            <p className="text-[11px] font-mono text-slate-400 truncate">
              {subtitle}
            </p>
          </>
        ) : (
          <div className="w-full" />
        )}
      </div>
    </CyberCard>
  );
}
