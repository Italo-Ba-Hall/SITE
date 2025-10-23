import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const [isYouTubeHovered, setIsYouTubeHovered] = useState(false);
  const [isTaxHovered, setIsTaxHovered] = useState(false);
  const [isAnimationComplete, setIsAnimationComplete] = useState(false);
  const location = useLocation();

  // Renderiza navbar simplificada no Playground
  const isPlayground = location.pathname === '/playground';

  // Escutar evento de animação completa
  useEffect(() => {
    const handleShowMainContent = () => {
      setIsAnimationComplete(true);
    };

    // Verificar se a animação já foi exibida
    const introShown = sessionStorage.getItem('introShown');
    if (introShown === 'true') {
      setIsAnimationComplete(true);
    }

    window.addEventListener('showMainContent', handleShowMainContent);
    
    return () => {
      window.removeEventListener('showMainContent', handleShowMainContent);
    };
  }, []);

  // Não renderizar navbar durante a animação
  if (!isAnimationComplete) {
    return null;
  }

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 10000, /* Menor que a navbar interna (10001) */
        padding: '1rem',
        pointerEvents: 'none',
        backgroundColor: 'transparent'
      }}
    >
      <div style={{
        display: 'flex',
        justifyContent: isPlayground ? 'center' : 'space-between',
        alignItems: 'center',
        maxWidth: '100%',
        pointerEvents: 'auto',
        gap: '1rem',
        marginTop: (isPlayground || location.pathname === '/') ? '0' : '80px' /* Só aplica margin na página fiscal */
      }}>
        {/* Botões específicos para Playground */}
        {isPlayground ? (
          <>
            <Link
              to="/"
              onMouseEnter={() => setIsYouTubeHovered(true)}
              onMouseLeave={() => setIsYouTubeHovered(false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                background: isYouTubeHovered
                  ? 'rgba(0, 229, 255, 0.1)'
                  : 'rgba(8, 8, 8, 0.6)',
                border: isYouTubeHovered
                  ? '1px solid rgba(0, 229, 255, 0.4)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '0.5rem',
                textDecoration: 'none',
                fontFamily: '"Courier New", Courier, monospace',
                fontSize: '0.85rem',
                fontWeight: 400,
                letterSpacing: '0.05em',
                transition: 'all 0.3s ease',
                boxShadow: isYouTubeHovered
                  ? '0 0 15px rgba(0, 229, 255, 0.3)'
                  : 'none',
                backdropFilter: 'blur(5px)'
              }}
            >
              <span style={{
                fontSize: '1.5rem',
                filter: isYouTubeHovered
                  ? 'drop-shadow(0 0 8px rgba(0, 229, 255, 0.8))'
                  : 'drop-shadow(0 0 4px rgba(0, 229, 255, 0.4))',
                transition: 'all 0.3s ease'
              }}>
                🏠
              </span>
              <span style={{
                color: isYouTubeHovered ? '#00e5ff' : '#ffffff',
                transition: 'color 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                whiteSpace: 'nowrap'
              }}>
                [ &gt; home ]
                {isYouTubeHovered && (
                  <span style={{
                    marginLeft: '0.25rem',
                    animation: 'blink 1s infinite',
                    color: '#00e5ff'
                  }}>
                    _
                  </span>
                )}
              </span>
            </Link>

            <Link
              to="/fiscal-reports"
              onMouseEnter={() => setIsTaxHovered(true)}
              onMouseLeave={() => setIsTaxHovered(false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                background: isTaxHovered
                  ? 'rgba(102, 126, 234, 0.1)'
                  : 'rgba(8, 8, 8, 0.6)',
                border: isTaxHovered
                  ? '1px solid rgba(102, 126, 234, 0.4)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '0.5rem',
                textDecoration: 'none',
                fontFamily: '"Courier New", Courier, monospace',
                fontSize: '0.85rem',
                fontWeight: 400,
                letterSpacing: '0.05em',
                transition: 'all 0.3s ease',
                boxShadow: isTaxHovered
                  ? '0 0 15px rgba(102, 126, 234, 0.3)'
                  : 'none',
                backdropFilter: 'blur(5px)'
              }}
            >
              <span style={{
                fontSize: '1.5rem',
                filter: isTaxHovered
                  ? 'drop-shadow(0 0 8px rgba(102, 126, 234, 0.8))'
                  : 'drop-shadow(0 0 4px rgba(102, 126, 234, 0.4))',
                transition: 'all 0.3s ease'
              }}>
                📊
              </span>
              <span style={{
                color: isTaxHovered ? '#667eea' : '#ffffff',
                transition: 'color 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                whiteSpace: 'nowrap'
              }}>
                [ &gt; fiscal_reports ]
                {isTaxHovered && (
                  <span style={{
                    marginLeft: '0.25rem',
                    animation: 'blink 1s infinite',
                    color: '#667eea'
                  }}>
                    _
                  </span>
                )}
              </span>
            </Link>
          </>
        ) : (
          <>
            {/* YouTube Playground Button - Left */}
            <Link
          to="/playground"
          onMouseEnter={() => setIsYouTubeHovered(true)}
          onMouseLeave={() => setIsYouTubeHovered(false)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: isYouTubeHovered
              ? 'rgba(6, 182, 212, 0.1)'
              : 'rgba(8, 8, 8, 0.6)',
            border: isYouTubeHovered
              ? '1px solid rgba(6, 182, 212, 0.4)'
              : '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontFamily: '"Courier New", Courier, monospace',
            fontSize: '0.85rem',
            fontWeight: 400,
            letterSpacing: '0.05em',
            transition: 'all 0.3s ease',
            boxShadow: isYouTubeHovered
              ? '0 0 15px rgba(6, 182, 212, 0.3)'
              : 'none',
            backdropFilter: 'blur(5px)'
          }}
        >
          {/* YouTube Icon */}
          <svg
            width="32"
            height="24"
            viewBox="0 0 32 24"
            xmlns="http://www.w3.org/2000/svg"
            style={{
              flexShrink: 0,
              filter: isYouTubeHovered
                ? 'drop-shadow(0 0 10px rgba(255, 0, 0, 0.8))'
                : 'drop-shadow(0 0 5px rgba(255, 0, 0, 0.4))',
              transition: 'all 0.3s ease'
            }}
          >
            <rect x="0" y="0" width="32" height="24" rx="3" fill="#FF0000" />
            <polygon points="12,8 12,16 20,12" fill="#FFFFFF" />
          </svg>

          {/* Terminal Text */}
          <span style={{
            color: isYouTubeHovered ? '#00e5ff' : '#00e5ff', /* Sempre ciano */
            transition: 'color 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            whiteSpace: 'nowrap'
          }}>
            [ &gt; youtube_playground ]
            {isYouTubeHovered && (
              <span style={{
                marginLeft: '0.25rem',
                animation: 'blink 1s infinite',
                color: '#00e5ff'
              }}>
                _
              </span>
            )}
          </span>
        </Link>

        {/* TAX Intelligence Button or Back Button - Right */}
        {location.pathname === '/fiscal-reports' ? (
          <Link
            to="/"
            onMouseEnter={() => setIsTaxHovered(true)}
            onMouseLeave={() => setIsTaxHovered(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: isTaxHovered
                ? 'rgba(0, 229, 255, 0.1)'
                : 'rgba(8, 8, 8, 0.6)',
              border: isTaxHovered
                ? '1px solid rgba(0, 229, 255, 0.4)'
                : '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '0.5rem',
              textDecoration: 'none',
              fontFamily: '"Courier New", Courier, monospace',
              fontSize: '0.85rem',
              fontWeight: 400,
              letterSpacing: '0.05em',
              transition: 'all 0.3s ease',
              boxShadow: isTaxHovered
                ? '0 0 15px rgba(0, 229, 255, 0.3)'
                : 'none',
              backdropFilter: 'blur(5px)'
            }}
          >
            {/* Back Arrow */}
            <span style={{
              fontSize: '1.5rem',
              filter: isTaxHovered
                ? 'drop-shadow(0 0 8px rgba(0, 229, 255, 0.8))'
                : 'drop-shadow(0 0 4px rgba(0, 229, 255, 0.4))',
              transition: 'all 0.3s ease'
            }}>
              ←
            </span>

            {/* Terminal Text */}
            <span style={{
              color: isTaxHovered ? '#00e5ff' : '#ffffff',
              transition: 'color 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              whiteSpace: 'nowrap'
            }}>
              [ &lt; voltar ]
              {isTaxHovered && (
                <span style={{
                  marginLeft: '0.25rem',
                  animation: 'blink 1s infinite',
                  color: '#00e5ff'
                }}>
                  _
                </span>
              )}
            </span>
          </Link>
        ) : (
          <Link
            to="/fiscal-reports"
            onMouseEnter={() => setIsTaxHovered(true)}
            onMouseLeave={() => setIsTaxHovered(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: isTaxHovered
                ? 'rgba(102, 126, 234, 0.1)'
                : 'rgba(8, 8, 8, 0.6)',
              border: isTaxHovered
                ? '1px solid rgba(102, 126, 234, 0.4)'
                : '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '0.5rem',
              textDecoration: 'none',
              fontFamily: '"Courier New", Courier, monospace',
              fontSize: '0.85rem',
              fontWeight: 400,
              letterSpacing: '0.05em',
              transition: 'all 0.3s ease',
              boxShadow: isTaxHovered
                ? '0 0 15px rgba(102, 126, 234, 0.3)'
                : 'none',
              backdropFilter: 'blur(5px)'
            }}
          >
            {/* Icon */}
            <span style={{
              fontSize: '1.5rem',
              filter: isTaxHovered
                ? 'drop-shadow(0 0 8px rgba(102, 126, 234, 0.8))'
                : 'drop-shadow(0 0 4px rgba(102, 126, 234, 0.4))',
              transition: 'all 0.3s ease'
            }}>
              📊
            </span>

            {/* Terminal Text */}
            <span style={{
              color: isTaxHovered ? '#00e5ff' : '#00e5ff', /* Sempre ciano */
              transition: 'color 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              whiteSpace: 'nowrap'
            }}>
              [ &gt; tax_intelligence ]
              {isTaxHovered && (
                <span style={{
                  marginLeft: '0.25rem',
                  animation: 'blink 1s infinite',
                  color: '#00e5ff'
                }}>
                  _
                </span>
              )}
            </span>
          </Link>
        )}
          </>
        )}

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
