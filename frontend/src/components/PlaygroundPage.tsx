import React, { useState, useRef, useEffect } from "react";
import usePlayground from "../hooks/usePlayground";
import YouTube from "react-youtube";
import TranscriptionView from "./playground/TranscriptionView";
import SummaryView from "./playground/SummaryView";
import UserRegistrationModal from "./UserRegistrationModal";

const PlaygroundPage: React.FC = () => {
  const {
    videoId,
    transcript,
    segments,
    summary,
    loading,
    error,
    showRegistrationModal,
    handleUrlSubmit,
    handleSummarize,
    clearError,
    registerUser,
    updateExport,
    setShowRegistrationModal,
  } = usePlayground();

  const [urlInput, setUrlInput] = useState("");
  const playerRef = useRef<{ seekTo: (seconds: number, allowSeekAhead: boolean) => void } | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [videoSize, setVideoSize] = useState<"normal" | "large" | "fullwidth">("normal");
  const [viewMode, setViewMode] = useState<"transcript" | "summary" | "split">("transcript");
  const [splitRatio, setSplitRatio] = useState(50); // Percentual do lado esquerdo

  // Gerenciar responsividade
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Resetar viewMode quando videoId mudar (nova transcrição)
  useEffect(() => {
    setViewMode("transcript");
  }, [videoId]);

  const handleTranscribe = () => {
    if (urlInput.trim()) {
      handleUrlSubmit(urlInput.trim());
    }
  };

  const handleTimestampClick = (timestamp: number) => {
    try {
      if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
        playerRef.current.seekTo(timestamp, true);
      }
      // Warning removido: silenciar quando player não está pronto
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao navegar no vídeo:', error); // Log crítico para debug de falhas no player
    }
  };

  const handleExport = (format: 'txt' | 'pdf') => {
    if (format === 'txt') {
      // Criar TXT formatado
      let content = '';
      
      if (summary) {
        // Exportar Resumo
        content += '═══════════════════════════════════════════════════════════\n';
        content += '                    RESUMO INTELIGENTE\n';
        content += '═══════════════════════════════════════════════════════════\n\n';
        
        if (videoId) {
          content += `📹 Vídeo: https://www.youtube.com/watch?v=${videoId}\n`;
        }
        content += `✓ Confiança: ${(summary.confidence * 100).toFixed(0)}%\n\n`;
        
        content += '─── RESUMO GERAL ───\n\n';
        content += summary.summary + '\n\n';
        
        if (summary.key_points && summary.key_points.length > 0) {
          content += '─── PONTOS PRINCIPAIS ───\n\n';
          summary.key_points.forEach((point, index) => {
            content += `  ${index + 1}. ${point}\n`;
          });
          content += '\n';
        }
        
        if (summary.keywords_found && summary.keywords_found.length > 0) {
          content += '─── PALAVRAS-CHAVE ENCONTRADAS ───\n\n';
          content += summary.keywords_found.join(', ') + '\n\n';
        }
        
        if (summary.sections && summary.sections.length > 0) {
          content += '─── SEÇÕES TEMÁTICAS ───\n\n';
          summary.sections.forEach((section) => {
            content += `▸ ${section.title.toUpperCase()}\n`;
            content += section.content + '\n\n';
          });
        }
      } else if (transcript) {
        // Exportar Transcrição
        content += '═══════════════════════════════════════════════════════════\n';
        content += '                     TRANSCRIÇÃO\n';
        content += '═══════════════════════════════════════════════════════════\n\n';
        
        if (videoId) {
          content += `📹 Vídeo: https://www.youtube.com/watch?v=${videoId}\n\n`;
        }
        
        if (segments && segments.length > 0) {
          segments.forEach((segment) => {
            const mins = Math.floor(segment.start / 60);
            const secs = Math.floor(segment.start % 60);
            const timestamp = `${mins}:${secs.toString().padStart(2, '0')}`;
            content += `[${timestamp}] ${segment.text}\n\n`;
          });
        } else {
          content += transcript;
        }
      }
      
      // Download do arquivo
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const fileName = summary 
        ? `resumo_${videoId || 'video'}_${Date.now()}.txt`
        : `transcricao_${videoId || 'video'}_${Date.now()}.txt`;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      // Atualizar export no backend
      updateExport(format);
    }
  };

  return (
    <div className="content visible" style={{ top: "15%", transform: "translate(-50%, 0)", maxWidth: "1400px", width: "95%" }}>
      {/* Logo */}
      <div className="logo" style={{ marginBottom: "1rem" }}>YouTube Playground</div>
      <div className="subtitle" style={{ marginBottom: "2rem" }}>Transcrição e Sumarização</div>

      {/* Error Banner - Visual Amigável */}
      {error && (
        <div
          style={{
            backgroundColor: "rgba(220, 38, 38, 0.15)",
            border: "1px solid rgba(220, 38, 38, 0.5)",
            padding: "1rem",
            borderRadius: "6px",
            marginBottom: "1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            maxHeight: "120px",
            overflow: "hidden",
            boxShadow: "0 2px 8px rgba(220, 38, 38, 0.2)",
          }}
        >
          <div style={{ 
            flex: 1, 
            display: "flex", 
            alignItems: "flex-start", 
            gap: "0.75rem",
            maxHeight: "100px",
            overflowY: "auto"
          }}>
            <span style={{ 
              color: "#ff6b6b", 
              fontSize: "1.25rem",
              lineHeight: 1,
              marginTop: "2px"
            }}>
              ⚠️
            </span>
            <div style={{ flex: 1 }}>
              <p style={{ 
                color: "#ffffff", 
                fontSize: "0.9rem",
                margin: 0,
                lineHeight: 1.5,
                fontWeight: 500
              }}>
                {error}
              </p>
            </div>
          </div>
          <button
            onClick={clearError}
            style={{
              background: "rgba(255, 255, 255, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              borderRadius: "4px",
              color: "#ffffff",
              fontSize: "1.25rem",
              cursor: "pointer",
              padding: "0.25rem 0.5rem",
              marginLeft: "1rem",
              transition: "all 0.2s",
              flexShrink: 0
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
            }}
            title="Fechar"
          >
            ×
          </button>
        </div>
      )}

      {/* URL Input - Estilo da página principal */}
      <div className="prompt-container" style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span className="prompt-prefix">URL&gt;</span>
          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyUp={(e) => {
              if (e.key === "Enter" && urlInput.trim() && !loading) {
                handleTranscribe();
              }
            }}
            placeholder="Cole a URL do YouTube aqui"
            disabled={loading}
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "#ffffff",
              fontSize: "1rem",
              fontFamily: "'Roboto Mono', monospace",
            }}
          />
          {!loading && urlInput.trim() && (
            <button
              onClick={handleTranscribe}
              style={{
                background: "transparent",
                border: "1px solid #00e5ff",
                color: "#00e5ff",
                padding: "0.5rem 1rem",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.875rem",
                fontFamily: "'Roboto Mono', monospace",
                transition: "all 0.3s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(0, 229, 255, 0.1)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              Transcrever
            </button>
          )}
        </div>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div style={{ textAlign: "center", padding: "2rem 0" }}>
          <div
            style={{
              display: "inline-block",
              width: "40px",
              height: "40px",
              border: "3px solid rgba(0, 229, 255, 0.3)",
              borderTopColor: "#00e5ff",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          ></div>
          <p style={{ color: "#00e5ff", marginTop: "1rem", fontSize: "0.875rem" }}>
            Processando...
          </p>
        </div>
      )}

      {/* Video Player and Transcription/Summary */}
      {videoId && !loading && (
        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile 
            ? "1fr" 
            : (viewMode === "split" || videoSize === "fullwidth")
              ? "1fr" 
              : videoSize === "large" 
                ? "70% 30%" 
                : "60% 40%",
          gap: "1.5rem",
          marginBottom: "1.5rem"
        }}>
          {/* Video Player */}
          <div 
            className="prompt-container"
            style={{
              position: viewMode === "split" ? "relative" : (videoSize !== "fullwidth" && !isMobile ? "sticky" : "relative"),
              top: viewMode === "split" ? "0" : (videoSize !== "fullwidth" && !isMobile ? "2rem" : "0"),
              alignSelf: viewMode === "split" ? "stretch" : (videoSize !== "fullwidth" && !isMobile ? "start" : "stretch"),
              maxHeight: viewMode === "split" ? "none" : (videoSize !== "fullwidth" && !isMobile ? "calc(100vh - 4rem)" : "none"),
            }}
          >
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1rem"
            }}>
              <h2 style={{
                color: "#00e5ff",
                fontSize: "1.25rem",
                fontWeight: "700",
                margin: 0
              }}>
                Vídeo
              </h2>
              {!isMobile && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => setVideoSize("normal")}
                    style={{
                      padding: "0.25rem 0.5rem",
                      background: videoSize === "normal" ? "rgba(0, 229, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${videoSize === "normal" ? "#00e5ff" : "rgba(255, 255, 255, 0.1)"}`,
                      borderRadius: "3px",
                      color: videoSize === "normal" ? "#00e5ff" : "#999",
                      cursor: "pointer",
                      fontSize: "0.75rem",
                      transition: "all 0.2s"
                    }}
                    title="Tamanho normal (60%)"
                  >
                    Normal
                  </button>
                  <button
                    onClick={() => setVideoSize("large")}
                    style={{
                      padding: "0.25rem 0.5rem",
                      background: videoSize === "large" ? "rgba(0, 229, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${videoSize === "large" ? "#00e5ff" : "rgba(255, 255, 255, 0.1)"}`,
                      borderRadius: "3px",
                      color: videoSize === "large" ? "#00e5ff" : "#999",
                      cursor: "pointer",
                      fontSize: "0.75rem",
                      transition: "all 0.2s"
                    }}
                    title="Tamanho grande (70%)"
                  >
                    Grande
                  </button>
                  <button
                    onClick={() => setVideoSize("fullwidth")}
                    style={{
                      padding: "0.25rem 0.5rem",
                      background: videoSize === "fullwidth" ? "rgba(0, 229, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${videoSize === "fullwidth" ? "#00e5ff" : "rgba(255, 255, 255, 0.1)"}`,
                      borderRadius: "3px",
                      color: videoSize === "fullwidth" ? "#00e5ff" : "#999",
                      cursor: "pointer",
                      fontSize: "0.75rem",
                      transition: "all 0.2s"
                    }}
                    title="Largura completa (100%)"
                  >
                    Full
                  </button>
                </div>
              )}
            </div>
            <div
              style={{
                position: "relative",
                width: "100%",
                paddingBottom: viewMode === "split" ? "0" : "56.25%",
                height: viewMode === "split" ? "35vh" : undefined,
                backgroundColor: "#000",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <div style={{ position: "absolute", inset: 0 }}>
                <YouTube
                  videoId={videoId}
                  opts={{
                    width: "100%",
                    height: "100%",
                    playerVars: {
                      autoplay: 0,
                      modestbranding: 1,
                      rel: 0,
                    },
                  }}
                  style={{ width: "100%", height: "100%" }}
                  onReady={(event) => {
                    playerRef.current = event.target;
                  }}
                />
              </div>
            </div>
          </div>

          {/* Transcription or Summary */}
          <div 
            className="prompt-container"
            style={{
              maxHeight: viewMode === "split" 
                ? "calc(65vh - 4rem)"
                : (videoSize !== "fullwidth" && !isMobile ? "calc(100vh - 4rem)" : "none"),
              overflowY: viewMode === "split" ? "hidden" : (videoSize !== "fullwidth" && !isMobile ? "auto" : "visible"),
              padding: viewMode === "split" ? "0" : undefined,
            }}
          >
            {/* Header com botões de controle */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: viewMode === "split" ? "1rem" : "0 0 1rem 0",
              borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
              marginBottom: "1rem"
            }}>
              <h2 style={{
                color: "#00e5ff",
                fontSize: "1.25rem",
                fontWeight: "700",
                margin: 0
              }}>
                {viewMode === "transcript" ? "Transcrição" : viewMode === "summary" ? "Resumo" : "Transcrição & Resumo"}
              </h2>
              
              {summary && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => setViewMode("transcript")}
                    style={{
                      padding: "0.5rem 0.75rem",
                      background: viewMode === "transcript" ? "rgba(0, 229, 255, 0.3)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${viewMode === "transcript" ? "#00e5ff" : "rgba(255, 255, 255, 0.2)"}`,
                      borderRadius: "4px",
                      color: viewMode === "transcript" ? "#00e5ff" : "#fff",
                      cursor: "pointer",
                      fontSize: "0.8rem"
                    }}
                  >
                    Transcrição
                  </button>
                  <button
                    onClick={() => setViewMode("summary")}
                    style={{
                      padding: "0.5rem 0.75rem",
                      background: viewMode === "summary" ? "rgba(0, 229, 255, 0.3)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${viewMode === "summary" ? "#00e5ff" : "rgba(255, 255, 255, 0.2)"}`,
                      borderRadius: "4px",
                      color: viewMode === "summary" ? "#00e5ff" : "#fff",
                      cursor: "pointer",
                      fontSize: "0.8rem"
                    }}
                  >
                    Resumo
                  </button>
                  <button
                    onClick={() => setViewMode("split")}
                    style={{
                      padding: "0.5rem 0.75rem",
                      background: viewMode === "split" ? "rgba(0, 229, 255, 0.3)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${viewMode === "split" ? "#00e5ff" : "rgba(255, 255, 255, 0.2)"}`,
                      borderRadius: "4px",
                      color: viewMode === "split" ? "#00e5ff" : "#fff",
                      cursor: "pointer",
                      fontSize: "0.8rem"
                    }}
                  >
                    Ver Ambos
                  </button>
                </div>
              )}
            </div>

            {/* Content Area */}
            {viewMode === "split" && summary ? (
              <div style={{
                display: "flex",
                height: "calc(60vh - 4rem)",
                gap: "0.5rem",
                padding: "0 1rem 1rem 1rem"
              }}>
                {/* Transcrição */}
                <div style={{
                  width: `${splitRatio}%`,
                  overflowY: "auto",
                  paddingRight: "0.5rem",
                  borderRight: "1px solid rgba(255, 255, 255, 0.1)"
                }}>
                  <TranscriptionView
                    transcript={transcript}
                    segments={segments}
                  onSummarize={(context, keywords) => {
                    handleSummarize(context, keywords);
                    setViewMode("summary");
                  }}
                    onTimestampClick={handleTimestampClick}
                    loading={loading}
                    hasSummary={false}
                    onExport={handleExport}
                  />
                </div>

                {/* Resize Handle */}
                <div
                  onMouseDown={(e) => {
                    e.preventDefault();
                    const container = e.currentTarget.parentElement;
                    if (!container) return;
                    
                    const startX = e.clientX;
                    const startRatio = splitRatio;
                    
                    const handleMouseMove = (e: MouseEvent) => {
                      const deltaX = e.clientX - startX;
                      const containerWidth = container.offsetWidth;
                      const deltaPercent = (deltaX / containerWidth) * 100;
                      const newRatio = Math.min(Math.max(startRatio + deltaPercent, 30), 70);
                      setSplitRatio(newRatio);
                    };
                    
                    const handleMouseUp = () => {
                      document.removeEventListener('mousemove', handleMouseMove);
                      document.removeEventListener('mouseup', handleMouseUp);
                    };
                    
                    document.addEventListener('mousemove', handleMouseMove);
                    document.addEventListener('mouseup', handleMouseUp);
                  }}
                  style={{
                    width: "4px",
                    cursor: "col-resize",
                    background: "rgba(0, 212, 255, 0.3)",
                    borderRadius: "2px",
                    transition: "background 0.2s",
                  }}
                  onMouseEnter={(e) => {e.currentTarget.style.background = "rgba(0, 212, 255, 0.6)";}}
                  onMouseLeave={(e) => {e.currentTarget.style.background = "rgba(0, 212, 255, 0.3)";}}
                />

                {/* Resumo */}
                <div style={{
                  width: `${100 - splitRatio}%`,
                  overflowY: "auto",
                  paddingLeft: "0.5rem"
                }}>
                  <div>
                    {summary.was_truncated && (
                      <div style={{
                        padding: "0.75rem",
                        background: "rgba(255, 165, 0, 0.1)",
                        border: "1px solid rgba(255, 165, 0, 0.3)",
                        borderRadius: "4px",
                        color: "#ffa500",
                        fontSize: "0.875rem",
                        marginBottom: "1rem"
                      }}>
                        ⚠️ Transcrição muito longa. Resumo baseado nos primeiros segmentos.
                      </div>
                    )}
                    <SummaryView summary={summary} onExport={handleExport} />
                  </div>
                </div>
              </div>
            ) : viewMode === "transcript" || !summary ? (
              <div style={{ padding: viewMode === "split" ? "0 1rem 1rem 1rem" : "0" }}>
                <TranscriptionView
                  transcript={transcript}
                  segments={segments}
                  onSummarize={(context, keywords) => {
                    handleSummarize(context, keywords);
                    setViewMode("summary");
                  }}
                  onTimestampClick={handleTimestampClick}
                  loading={loading}
                  hasSummary={summary !== null}
                  onViewSummary={() => setViewMode("summary")}
                  onExport={handleExport}
                />
              </div>
            ) : (
              <div style={{ padding: viewMode === "split" ? "0 1rem 1rem 1rem" : "0" }}>
                {summary.was_truncated && (
                  <div style={{
                    padding: "0.75rem",
                    background: "rgba(255, 165, 0, 0.1)",
                    border: "1px solid rgba(255, 165, 0, 0.3)",
                    borderRadius: "4px",
                    color: "#ffa500",
                    fontSize: "0.875rem",
                    marginBottom: "1rem"
                  }}>
                    ⚠️ Transcrição muito longa. Resumo baseado nos primeiros segmentos.
                  </div>
                )}
                <SummaryView summary={summary} />
              </div>
            )}
          </div>
        </div>
      )}


      {/* Empty State */}
      {!videoId && !loading && (
        <div style={{ textAlign: "center", padding: "2rem 0" }}>
          <div style={{ color: "#666666", fontSize: "0.875rem" }}>
            Já se divertiu hoje? =D
          </div>
        </div>
      )}

      {/* Keyframes for spin animation */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>

      {/* Modal de Registro */}
      <UserRegistrationModal
        isOpen={showRegistrationModal}
        onClose={() => setShowRegistrationModal(false)}
        onSubmit={registerUser}
      />
    </div>
  );
};

export default PlaygroundPage;
