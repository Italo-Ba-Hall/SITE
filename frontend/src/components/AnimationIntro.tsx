import React, { useEffect, useRef, useState, useCallback } from 'react';

const AnimationIntro: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const svgRef = useRef<SVGSVGElement>(null);
  const animationCompleteRef = useRef(false);

  const animateElement = useCallback((el: Element, delay: number, duration: number): Promise<void> => {
    return new Promise(resolve => {
      setTimeout(() => {
        const element = el as SVGPathElement | SVGTextElement;
        element.style.transition = `stroke-dashoffset ${duration / 1000}s ease-in-out, opacity ${duration / 1000}s ease-in-out`;
        if (element.tagName === 'path') {
          (element as SVGPathElement).style.strokeDashoffset = '0';
        }
        element.style.opacity = '1';
        setTimeout(resolve, duration);
      }, delay);
    });
  }, []);

  const typeWriter = useCallback((el: SVGTextElement, delay: number): Promise<void> => {
    return new Promise(resolve => {
      setTimeout(() => {
        const text = el.textContent || '';
        el.textContent = '';
        el.style.opacity = '1';
        let i = 0;
        const interval = setInterval(() => {
          if (i < text.length) {
            el.textContent += text.charAt(i);
            i++;
          } else {
            clearInterval(interval);
            resolve();
          }
        }, 80);
      }, delay);
    });
  }, []);

  useEffect(() => {
    if (animationCompleteRef.current) return;

    const runIntroAnimation = async () => {
      const svg = svgRef.current;
      if (!svg) return;

      // Preparar elementos para animação
      const elementsToAnimate = Array.from(svg.querySelectorAll('path, text')).filter(Boolean);
      elementsToAnimate.forEach(el => {
        const element = el as SVGPathElement | SVGTextElement;
        if (element.tagName === 'path') {
          const pathElement = element as SVGPathElement;
          const length = pathElement.getTotalLength();
          pathElement.style.strokeDasharray = `${length}`;
          pathElement.style.strokeDashoffset = `${length}`;
        }
        element.style.opacity = '0';
      });

      // Sequência de animação
      const fastDuration = 500;
      const spiralDuration = 1500;

      const groups = ['#linhas-construcao path', '#quadrados-solidos path', '#numeros text'];
      const delays = [20, 40, 60];

      // Animar grupos sequencialmente
      for (let i = 0; i < groups.length; i++) {
        const elements = Array.from(svg.querySelectorAll(groups[i]));
        let groupDelay = 0;
        for (const el of elements) {
          animateElement(el, groupDelay, fastDuration);
          groupDelay += delays[i];
        }
        await new Promise(r => setTimeout(r, groupDelay + fastDuration));
      }

      // Animar espiral
      let spiralDelay = 0;
      const spiralPaths = Array.from(svg.querySelectorAll('#espiral path'));
      for (const path of spiralPaths) {
        animateElement(path, spiralDelay, spiralDuration);
        spiralDelay += 100;
      }
      await new Promise(r => setTimeout(r, spiralDelay + spiralDuration));

      // Animar texto do slogan
      const sloganText = svg.querySelector('#slogan-text') as SVGTextElement;
      if (sloganText) {
        await typeWriter(sloganText, 0);
      }

      // Animar cursor
      const cursor = svg.querySelector('#slogan-cursor') as SVGRectElement;
      if (cursor) {
        cursor.style.opacity = '1';
        await new Promise(r => setTimeout(r, 400));
        cursor.style.opacity = '0';
        await new Promise(r => setTimeout(r, 400));
        cursor.style.opacity = '1';
        await new Promise(r => setTimeout(r, 400));
        cursor.style.opacity = '0';
        await new Promise(r => setTimeout(r, 200));
      }

      // Aguardar um pouco antes de finalizar
      await new Promise(r => setTimeout(r, 1000));

      // Finalizar animação com transição suave
      setIsVisible(false);
      
      // Disparar evento para mudança de modo de animação
      const event = new CustomEvent('animationModeChange', { detail: { mode: 'circuit' } });
      window.dispatchEvent(event);
      
      // Disparar evento para exibir conteúdo principal
      const contentEvent = new CustomEvent('showMainContent');
      window.dispatchEvent(contentEvent);

      animationCompleteRef.current = true;
    };

    runIntroAnimation();
  }, [animateElement, typeWriter]);

  return (
    <div className={`animation-container ${!isVisible ? 'hidden' : ''}`}>
      <svg
        ref={svgRef}
        id="fibonacci-svg"
        viewBox="250 200 450 350"
        preserveAspectRatio="xMidYMid meet"
        xmlns="http://www.w3.org/2000/svg"
      >
        <style>
          {`
            path {
              stroke: #ffffff;
              stroke-width: 3;
              fill: none;
              opacity: 0;
            }
            text {
              font-family: 'Roboto Mono', monospace;
              font-size: 24px;
              fill: #ffffff;
              stroke: none;
              opacity: 0;
              font-weight: bold;
            }
            #slogan text {
              font-size: 14px; 
              fill: #ffffff;
              text-anchor: middle;
              opacity: 0;
            }
            #slogan-cursor {
              opacity: 0;
            }
          `}
        </style>
        <g id="linhas-construcao" strokeDasharray="4, 4">
          <path d="M 300,250 L 650,250"/>
          <path d="M 650,250 L 650,500"/>
          <path d="M 300,500 L 650,500"/>
          <path d="M 300,250 L 300,500"/>
          <path d="M 400,400 L 430,405"/>
          <path d="M 430,405 L 390,445"/>
          <path d="M 390,445 L 400,400"/>
          <path d="M 390,445 L 325,380"/>
          <path d="M 325,380 L 430,275"/>
          <path d="M 430,275 L 390,445"/>
        </g>
        <g id="quadrados-solidos">
          <path d="M 400,400 L 405,400 L 405,405 L 400,405 Z"/>
          <path d="M 400,400 L 390,400 L 390,390 L 400,390 Z"/>
          <path d="M 405,405 L 430,405 L 430,380 L 405,380 Z"/>
          <path d="M 390,445 L 430,445 L 430,405 L 390,405 Z"/>
          <path d="M 390,445 L 325,445 L 325,380 L 390,380 Z"/>
        </g>
        <g id="numeros">
          <text x="410" y="395">5</text>
          <text x="370" y="420">13</text>
          <text x="350" y="360">21</text>
          <text x="450" y="330">34</text>
        </g>
        <g id="espiral">
          <path d="M 400,400 m -5,0 a 5,5 0 1,1 10,0 a 5,5 0 1,1 -10,0"/>
          <path d="M 405,400 A 5,5 0 0,1 400,405"/>
          <path d="M 400,405 A 10,10 0 0,1 390,395"/>
          <path d="M 390,395 A 15,15 0 0,1 405,380"/>
          <path d="M 405,380 A 25,25 0 0,1 430,405"/>
          <path d="M 430,405 A 40,40 0 0,1 390,445"/>
          <path d="M 390,445 A 65,65 0 0,1 325,380"/>
          <path d="M 325,380 A 105,105 0 0,1 430,275"/>
          <path d="M 430,275 A 170,170 0 0,1 600,445"/>
        </g>
        <g id="slogan">
          <text id="slogan-text" x="475" y="490">CODE, the new religion</text>
          <rect id="slogan-cursor" x="585" y="482" width="5" height="10" fill="#ffffff" opacity="0"/>
        </g>
      </svg>
    </div>
  );
};

export default AnimationIntro; 