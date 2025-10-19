import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);
  const location = useLocation();

  // Não renderiza o Navbar na página do Playground
  if (location.pathname === '/playground') {
    return null;
  }

  return (
    <nav 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        padding: '1.5rem',
        pointerEvents: 'none'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'center', pointerEvents: 'auto' }}>
        {/* YouTube Playground Button - Terminal Style */}
        <Link
          to="/playground"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem 1.5rem',
            background: isHovered 
              ? 'rgba(6, 182, 212, 0.1)' 
              : 'transparent',
            border: isHovered 
              ? '1px solid rgba(6, 182, 212, 0.5)' 
              : '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontFamily: '"Courier New", Courier, monospace',
            fontSize: '0.95rem',
            fontWeight: 500,
            letterSpacing: '0.05em',
            transition: 'all 0.3s ease',
            boxShadow: isHovered 
              ? '0 0 20px rgba(6, 182, 212, 0.3)' 
              : 'none',
            backdropFilter: isHovered ? 'blur(10px)' : 'none'
          }}
        >
          {/* YouTube Icon - Simple & Guaranteed */}
          <svg
            width="32"
            height="24"
            viewBox="0 0 32 24"
            xmlns="http://www.w3.org/2000/svg"
            style={{
              flexShrink: 0,
              filter: isHovered 
                ? 'drop-shadow(0 0 10px rgba(255, 0, 0, 0.8))' 
                : 'drop-shadow(0 0 5px rgba(255, 0, 0, 0.4))',
              transition: 'all 0.3s ease'
            }}
          >
            {/* Red rounded rectangle */}
            <rect x="0" y="0" width="32" height="24" rx="3" fill="#FF0000"/>
            {/* White play triangle */}
            <polygon points="12,8 12,16 20,12" fill="#FFFFFF"/>
          </svg>

          {/* Terminal Text */}
          <span style={{
            color: isHovered ? '#06b6d4' : '#ffffff',
            transition: 'color 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            whiteSpace: 'nowrap'
          }}>
            [ &gt; youtube_playground ]
            {isHovered && (
              <span style={{
                marginLeft: '0.25rem',
                animation: 'blink 1s infinite',
                color: '#06b6d4'
              }}>
                _
              </span>
            )}
          </span>
        </Link>

        {/* Keyframe Animation for Cursor */}
        <style>{`
          @keyframes blink {
            0%, 49% { opacity: 1; }
            50%, 100% { opacity: 0; }
          }
        `}</style>
      </div>
    </nav>
  );
};

export default Navbar;
