import { useEffect, useRef } from "react";

/**
 * Port of reel-engine's BrandBackground (aurora blobs + ambient particles) to a
 * plain rAF canvas — signature moment #2 (design-system.md §7). Edges stay
 * static (base gradient, stripes, vignette as CSS layers); motion lives in the
 * interior canvas only.
 */

const BLOBS = [
  { x: 24, y: 26, r: 560, hue: "#208EC7", ax: 60, ay: 40, sp: 0.45, ph: 0 },
  { x: 78, y: 70, r: 620, hue: "#1F5B99", ax: 70, ay: 55, sp: 0.38, ph: 2.1 },
  { x: 60, y: 18, r: 420, hue: "#208EC7", ax: 50, ay: 35, sp: 0.55, ph: 4.2 },
];

// Deterministic particles — same seeding math as the reel-engine reference.
const PARTICLES = Array.from({ length: 22 }, (_, i) => {
  const seed = (n: number) => ((((Math.sin((i + 1) * 12.9898 * n) * 43758.5453) % 1) + 1) % 1);
  return {
    x: seed(1) * 100,
    yBase: seed(2) * 100,
    size: 2 + seed(3) * 4,
    speed: 4 + seed(4) * 9,
    drift: (seed(5) - 0.5) * 6,
    twinkle: 2 + seed(6) * 3,
    blue: seed(7) > 0.5,
  };
});

function rgba(hex: string, a: number): string {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a.toFixed(3)})`;
}

export default function AuroraBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let w = 0;
    let h = 0;
    let raf = 0;
    const scale = Math.min(window.devicePixelRatio || 1, 1.25); // soft scene, no retina needed
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const resize = () => {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = Math.round(w * scale);
      canvas.height = Math.round(h * scale);
      ctx.setTransform(scale, 0, 0, scale, 0, 0);
      if (reduced) draw(0);
    };

    const draw = (t: number) => {
      ctx.clearRect(0, 0, w, h);
      const rScale = Math.min(1.4, Math.max(0.6, w / 1400));

      ctx.globalCompositeOperation = "lighter";
      for (const b of BLOBS) {
        const dx = Math.sin(t * b.sp + b.ph) * b.ax;
        const dy = Math.cos(t * b.sp * 0.8 + b.ph) * b.ay;
        const s = 1 + 0.12 * Math.sin(t * b.sp * 1.3 + b.ph);
        const op = 0.22 + 0.12 * Math.sin(t * b.sp + b.ph * 1.7);
        const cx = (b.x / 100) * w + dx;
        const cy = (b.y / 100) * h + dy;
        const R = b.r * rScale * s;
        const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, R);
        g.addColorStop(0, rgba(b.hue, Math.max(0, op) * 0.55));
        g.addColorStop(0.68, rgba(b.hue, Math.max(0, op) * 0.12));
        g.addColorStop(1, rgba(b.hue, 0));
        ctx.fillStyle = g;
        ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
      }

      ctx.globalCompositeOperation = "source-over";
      for (let i = 0; i < PARTICLES.length; i++) {
        const p = PARTICLES[i];
        const y = (((p.yBase - t * p.speed) % 100) + 100) % 100;
        const x = p.x + Math.sin(t * 0.6 + i) * p.drift;
        const tw = 0.25 + 0.55 * Math.abs(Math.sin(t / p.twinkle + i));
        const edgeFade = Math.min(1, y / 12, (100 - y) / 12);
        ctx.beginPath();
        ctx.arc((x / 100) * w, (y / 100) * h, p.size / 2, 0, Math.PI * 2);
        ctx.fillStyle = p.blue ? rgba("#208EC7", tw * 0.5 * edgeFade) : rgba("#FFFFFF", tw * 0.5 * edgeFade);
        ctx.fill();
      }
    };

    let running = true;
    const loop = (now: number) => {
      if (!running) return;
      draw(now / 1000);
      raf = requestAnimationFrame(loop);
    };

    const onVisibility = () => {
      running = !document.hidden && !reduced;
      if (running) raf = requestAnimationFrame(loop);
      else cancelAnimationFrame(raf);
    };

    resize();
    window.addEventListener("resize", resize);
    document.addEventListener("visibilitychange", onVisibility);
    if (reduced) draw(0);
    else raf = requestAnimationFrame(loop);

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-0 pointer-events-none" aria-hidden="true">
      {/* static charcoal base */}
      <div
        className="absolute inset-0"
        style={{ background: "linear-gradient(180deg, #161616 0%, #0B0B0B 100%)" }}
      />
      {/* aurora + particles */}
      <canvas ref={canvasRef} className="absolute inset-0" />
      {/* static diagonal stripe texture (brand motif) */}
      <div
        className="absolute inset-0"
        style={{
          opacity: 0.7,
          backgroundImage: `repeating-linear-gradient(135deg, transparent 0px, transparent 94px, rgba(0,0,0,0.55) 94px, rgba(0,0,0,0.55) 95px, transparent 95px, transparent 158px, rgba(32,142,199,0.07) 158px, rgba(32,142,199,0.07) 159px)`,
        }}
      />
      {/* frosted veil + static vignette — anchors the edges */}
      <div className="absolute inset-0" style={{ background: "rgba(11,11,11,0.30)" }} />
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(78% 62% at 50% 44%, transparent 38%, rgba(0,0,0,0.6) 100%)",
        }}
      />
    </div>
  );
}
