import { useState, useRef } from 'react';

/**
 * CyberCard — Refined Minimalist Dark Glass Card.
 * Clean, subtle, modern (Linear/Vercel style) without overdone neon or heavy decoration.
 */
export default function CyberCard({
  children,
  className = '',
  onClick,
  style = {},
  noPadding = false,
}) {
  const cardRef = useRef(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0, opacity: 0 });

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      opacity: 1,
    });
  };

  const handleMouseLeave = () => {
    setMousePos((prev) => ({ ...prev, opacity: 0 }));
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={`relative rounded-xl transition-all duration-200 overflow-hidden ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
      style={{
        background: 'rgba(13, 16, 28, 0.75)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.35)',
        ...style,
      }}
    >
      {/* Subtle top light edge */}
      <div
        className="absolute top-0 left-0 right-0 h-[1px] pointer-events-none z-10"
        style={{
          background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent)',
        }}
      />

      {/* Very soft, clean cursor spotlight (non-overdone) */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-300 z-0"
        style={{
          opacity: mousePos.opacity,
          background: `radial-gradient(450px circle at ${mousePos.x}px ${mousePos.y}px, rgba(255, 255, 255, 0.035), transparent 65%)`,
        }}
      />

      <div className={`relative z-10 w-full h-full ${noPadding ? '' : 'p-5'}`}>{children}</div>
    </div>
  );
}
