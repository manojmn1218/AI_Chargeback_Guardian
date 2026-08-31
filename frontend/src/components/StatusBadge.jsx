/**
 * StatusBadge — Cyber-styled risk/status badge with glow dot indicator.
 */
export default function StatusBadge({ status, type = 'risk' }) {
  const getStyles = () => {
    const s = status?.toLowerCase();

    if (type === 'risk') {
      switch (s) {
        case 'high':
          return {
            bg: 'rgba(239, 68, 68, 0.1)',
            border: 'rgba(239, 68, 68, 0.25)',
            color: '#ef4444',
            glow: '0 0 8px rgba(239, 68, 68, 0.3)',
            label: 'High Risk',
          };
        case 'medium':
          return {
            bg: 'rgba(245, 158, 11, 0.1)',
            border: 'rgba(245, 158, 11, 0.25)',
            color: '#f59e0b',
            glow: '0 0 8px rgba(245, 158, 11, 0.3)',
            label: 'Medium Risk',
          };
        case 'low':
          return {
            bg: 'rgba(34, 197, 94, 0.1)',
            border: 'rgba(34, 197, 94, 0.25)',
            color: '#22c55e',
            glow: '0 0 8px rgba(34, 197, 94, 0.3)',
            label: 'Low Risk',
          };
        default:
          return {
            bg: 'rgba(59, 130, 246, 0.1)',
            border: 'rgba(59, 130, 246, 0.25)',
            color: '#3b82f6',
            glow: '0 0 8px rgba(59, 130, 246, 0.3)',
            label: status || 'Unknown',
          };
      }
    }

    switch (s) {
      case 'open':
        return {
          bg: 'rgba(245, 158, 11, 0.1)',
          border: 'rgba(245, 158, 11, 0.25)',
          color: '#f59e0b',
          glow: '0 0 8px rgba(245, 158, 11, 0.3)',
          label: 'Open',
        };
      case 'under_review':
        return {
          bg: 'rgba(99, 102, 241, 0.1)',
          border: 'rgba(99, 102, 241, 0.25)',
          color: '#818cf8',
          glow: '0 0 8px rgba(99, 102, 241, 0.3)',
          label: 'Under Review',
        };
      case 'resolved':
        return {
          bg: 'rgba(34, 197, 94, 0.1)',
          border: 'rgba(34, 197, 94, 0.25)',
          color: '#22c55e',
          glow: '0 0 8px rgba(34, 197, 94, 0.3)',
          label: 'Resolved',
        };
      case 'closed':
        return {
          bg: 'rgba(100, 116, 139, 0.1)',
          border: 'rgba(100, 116, 139, 0.2)',
          color: '#94a3b8',
          glow: 'none',
          label: 'Closed',
        };
      default:
        return {
          bg: 'rgba(59, 130, 246, 0.1)',
          border: 'rgba(59, 130, 246, 0.25)',
          color: '#3b82f6',
          glow: '0 0 8px rgba(59, 130, 246, 0.3)',
          label: status || 'Unknown',
        };
    }
  };

  const styles = getStyles();

  return (
    <span
      className="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider"
      style={{
        backgroundColor: styles.bg,
        color: styles.color,
        border: `1px solid ${styles.border}`,
        boxShadow: styles.glow,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full mr-2 animate-pulse"
        style={{
          backgroundColor: styles.color,
          boxShadow: `0 0 6px ${styles.color}`,
        }}
      />
      {styles.label}
    </span>
  );
}
