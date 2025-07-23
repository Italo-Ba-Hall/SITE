import React, { useEffect, useRef } from 'react';

interface RainParticle {
  x: number;
  y: number;
  speed: number;
}

interface CircuitParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

const BackgroundCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationModeRef = useRef<'rain' | 'circuit'>('rain');
  const rainParticlesRef = useRef<RainParticle[]>([]);
  const circuitParticlesRef = useRef<CircuitParticle[]>([]);
  const animationIdRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    const setupRain = () => {
      rainParticlesRef.current = [];
      const columnCount = Math.floor(width / 20);
      for (let i = 0; i < columnCount; i++) {
        rainParticlesRef.current.push({
          x: i * 20,
          y: Math.random() * height,
          speed: 0.5 + Math.random() * 2
        });
      }
    };

    const setupCircuits = () => {
      circuitParticlesRef.current = [];
      const particleCount = Math.floor((width * height) / 20000);
      for (let i = 0; i < particleCount; i++) {
        circuitParticlesRef.current.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: 1.5 + Math.random() * 1
        });
      }
    };

    const drawNumberRain = () => {
      ctx.fillStyle = 'rgba(8, 8, 8, 0.1)';
      ctx.fillRect(0, 0, width, height);
      ctx.font = '16px Roboto Mono';
      ctx.fillStyle = 'rgba(0, 229, 255, 0.2)';
      
      for (const p of rainParticlesRef.current) {
        const char = Math.random() > 0.5 ? '0' : '1';
        ctx.fillText(char, p.x, p.y);
        p.y += p.speed;
        if (p.y > height) p.y = 0;
      }
    };

    const drawPulsatingCircuits = () => {
      ctx.fillStyle = 'rgba(8, 8, 8, 0.1)';
      ctx.fillRect(0, 0, width, height);

      const particles = circuitParticlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        const p1 = particles[i];
        p1.x += p1.vx;
        p1.y += p1.vy;
        
        if (p1.x < 0 || p1.x > width) p1.vx *= -1;
        if (p1.y < 0 || p1.y > height) p1.vy *= -1;

        ctx.beginPath();
        ctx.arc(p1.x, p1.y, p1.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.8)';
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 229, 255, ${1 - dist / 150})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
    };

    const animateBackground = () => {
      if (animationModeRef.current === 'rain') {
        drawNumberRain();
      } else {
        drawPulsatingCircuits();
      }
      animationIdRef.current = requestAnimationFrame(animateBackground);
    };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      setupRain();
      setupCircuits();
    };

    // Event listener para mudança de modo de animação
    const handleAnimationModeChange = (event: CustomEvent) => {
      animationModeRef.current = event.detail.mode;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('animationModeChange' as any, handleAnimationModeChange);

    setupRain();
    setupCircuits();
    animateBackground();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('animationModeChange' as any, handleAnimationModeChange);
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      id="backgroundCanvas"
      className="absolute top-0 left-0 z-5 transition-opacity duration-1000 ease-out"
    />
  );
};

export default BackgroundCanvas; 