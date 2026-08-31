import { useEffect, useRef } from 'react';

/**
 * CyberBackground — Refined Atmospheric Cyber Engine.
 * Opacity and brightness calibrated to be subtly deep and non-intrusive.
 */
export default function CyberBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    let animationId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let time = 0;
    const mouse = { x: width / 2, y: height / 2, targetX: width / 2, targetY: height / 2, active: false };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      initParticles();
    };

    const handleMouseMove = (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    // ==========================================
    // 1. NEURAL PARTICLE NETWORK (Subtle & Deep)
    // ==========================================
    let particles = [];
    const colors = [
      { r: 99, g: 102, b: 241 }, // Indigo
      { r: 139, g: 92, b: 246 }, // Violet
      { r: 6, g: 182, b: 212 },  // Cyan
      { r: 59, g: 130, b: 246 }, // Blue
    ];

    class NodeParticle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.baseX = this.x;
        this.baseY = this.y;
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = (Math.random() - 0.5) * 0.3;
        this.radius = Math.random() * 1.5 + 0.8;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.alpha = Math.random() * 0.25 + 0.08; // Calibrated lower brightness
        this.pulseSpeed = 0.015 + Math.random() * 0.015;
        this.pulsePhase = Math.random() * Math.PI * 2;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;

        if (mouse.active) {
          const dx = mouse.x - this.x;
          const dy = mouse.y - this.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const maxDist = 140;
          if (dist < maxDist) {
            const force = (1 - dist / maxDist) * 1.0;
            this.x += (dx / dist) * force;
            this.y += (dy / dist) * force;
          }
        }
      }

      draw() {
        const pulse = Math.sin(time * this.pulseSpeed + this.pulsePhase);
        const currentAlpha = Math.max(0.04, this.alpha + pulse * 0.08);
        const { r, g, b } = this.color;

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${currentAlpha * 0.12})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${currentAlpha})`;
        ctx.fill();
      }
    }

    function initParticles() {
      const count = Math.min(50, Math.floor((width * height) / 28000));
      particles = [];
      for (let i = 0; i < count; i++) {
        particles.push(new NodeParticle());
      }
    }
    initParticles();

    // ==========================================
    // 2. CIRCUIT LIGHT PACKETS
    // ==========================================
    const packets = [];
    for (let i = 0; i < 5; i++) {
      packets.push({
        p1: 0,
        p2: 1,
        progress: Math.random(),
        speed: 0.005 + Math.random() * 0.008,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    // ==========================================
    // 3. PERSPECTIVE 3D CYBER GRID (Softened)
    // ==========================================
    let gridOffset = 0;

    function drawPerspectiveGrid() {
      const horizonY = height * 0.7;
      const numLines = 12;
      gridOffset = (gridOffset + 0.2) % 24;

      ctx.save();
      ctx.beginPath();
      ctx.rect(0, horizonY, width, height - horizonY);
      ctx.clip();

      // Horizon line glow - soft & muted
      const horizonGrad = ctx.createLinearGradient(0, horizonY, 0, horizonY + 25);
      horizonGrad.addColorStop(0, 'rgba(99, 102, 241, 0.1)');
      horizonGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = horizonGrad;
      ctx.fillRect(0, horizonY, width, 40);

      // Horizontal lines receding into distance
      for (let i = 0; i < numLines; i++) {
        const d = (i * 20 + gridOffset) % (numLines * 20);
        const y = horizonY + (d * d) / (numLines * 7.5);
        if (y > height) continue;

        const lineAlpha = Math.min(0.08, ((y - horizonY) / (height - horizonY)) * 0.1);
        ctx.strokeStyle = `rgba(99, 102, 241, ${lineAlpha})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Perspective vertical lines meeting at center
      const centerX = width * 0.5;
      const vSpacing = 65;
      const vLines = Math.ceil(width / vSpacing) + 4;

      for (let i = -vLines; i <= vLines; i++) {
        const bottomX = centerX + i * vSpacing * 2.5;
        ctx.strokeStyle = `rgba(139, 92, 246, 0.04)`;
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(centerX + i * 2, horizonY);
        ctx.lineTo(bottomX, height);
        ctx.stroke();
      }

      ctx.restore();
    }

    // ==========================================
    // 4. RADAR HUD SWEEP (Low Luminance)
    // ==========================================
    let radarAngle = 0;

    function drawRadarHUD() {
      const radarCenter = { x: width * 0.84, y: height * 0.25 };
      const radarRadius = Math.min(150, width * 0.13);

      radarAngle = (radarAngle + 0.01) % (Math.PI * 2);

      ctx.save();
      ctx.translate(radarCenter.x, radarCenter.y);

      // Concentric circles
      for (let r of [radarRadius * 0.35, radarRadius * 0.7, radarRadius]) {
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.03)';
        ctx.lineWidth = 0.8;
        ctx.setLineDash([3, 5]);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // Rotating scanner beam
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, radarRadius, radarAngle - 0.35, radarAngle);
      ctx.lineTo(0, 0);
      const sweepGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, radarRadius);
      sweepGradient.addColorStop(0, 'rgba(6, 182, 212, 0.06)');
      sweepGradient.addColorStop(1, 'rgba(6, 182, 212, 0)');
      ctx.fillStyle = sweepGradient;
      ctx.fill();

      // Scanner beam line
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(radarAngle) * radarRadius, Math.sin(radarAngle) * radarRadius);
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.18)';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      ctx.restore();
    }

    // ==========================================
    // 5. MAIN ANIMATION LOOP
    // ==========================================
    function render() {
      time++;

      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      ctx.clearRect(0, 0, width, height);

      drawPerspectiveGrid();
      drawRadarHUD();

      for (let p of particles) {
        p.update();
        p.draw();
      }

      // Draw Network Interconnections (Subtle Alpha)
      const maxConnDist = 120;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxConnDist) {
            const alpha = (1 - dist / maxConnDist) * 0.07;
            const c1 = particles[i].color;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(${c1.r}, ${c1.g}, ${c1.b}, ${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      // Circuit Packets
      for (let pkt of packets) {
        if (particles.length < 2) continue;
        pkt.progress += pkt.speed;
        if (pkt.progress >= 1) {
          pkt.progress = 0;
          pkt.p1 = Math.floor(Math.random() * particles.length);
          let minDist = Infinity;
          let bestIdx = (pkt.p1 + 1) % particles.length;
          for (let k = 0; k < particles.length; k++) {
            if (k === pkt.p1) continue;
            const dx = particles[pkt.p1].x - particles[k].x;
            const dy = particles[pkt.p1].y - particles[k].y;
            const d = Math.sqrt(dx * dx + dy * dy);
            if (d < 140 && d < minDist) {
              minDist = d;
              bestIdx = k;
            }
          }
          pkt.p2 = bestIdx;
        }

        const pA = particles[pkt.p1];
        const pB = particles[pkt.p2];
        if (pA && pB) {
          const curX = pA.x + (pB.x - pA.x) * pkt.progress;
          const curY = pA.y + (pB.y - pA.y) * pkt.progress;
          const { r, g, b } = pkt.color;

          ctx.beginPath();
          ctx.arc(curX, curY, 1.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.5)`;
          ctx.fill();
        }
      }

      animationId = requestAnimationFrame(render);
    }

    render();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  );
}
