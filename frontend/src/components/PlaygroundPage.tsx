import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import usePlayground from "../hooks/usePlayground";
import YouTube from "react-youtube";
import TranscriptionView from "./playground/TranscriptionView";
import SummaryView from "./playground/SummaryView";

const PlaygroundPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    videoId,
    transcript,
    segments,
    summary,
    loading,
    error,
    handleUrlSubmit,
    handleSummarize,
    clearError,
    resetSummary,
  } = usePlayground();

  const [urlInput, setUrlInput] = useState("");
  const playerRef = useRef<{ seekTo: (seconds: number, allowSeekAhead: boolean) => void } | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  // Gerenciar responsividade
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleTranscribe = () => {
    if (urlInput.trim()) {
      handleUrlSubmit(urlInput.trim());
    }
  };

  const handleTimestampClick = (timestamp: number) => {
    try {
      if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
        playerRef.current.seekTo(timestamp, true);
      } else {
        console.warn('Player não está pronto para navegação');
      }
    } catch (error) {
      console.error('Erro ao navegar no vídeo:', error);
    }
  };

  return (
    <div className="content visible" style={{ top: "5%", transform: "translate(-50%, 0)", maxWidth: "900px", width: "95%" }}>
      {/* Botão Voltar - Canto Superior Direito */}
      <button
        onClick={() => navigate("/")}
        className="prompt-prefix"
        style={{
          position: "fixed",
          top: "2rem",
          right: "-5rem",
          zIndex: 100,
          fontSize: "0.875rem",
          background: "transparent",
          border: "1px solid #00e5ff",
          color: "#00e5ff",
          padding: "0.5rem 1rem",
          borderRadius: "4px",
          cursor: "pointer",
          transition: "all 0.3s",
          fontFamily: "'Roboto Mono', monospace",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = "rgba(0, 229, 255, 0.1)";
          e.currentTarget.style.color = "#00b8cc";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = "transparent";
          e.currentTarget.style.color = "#00e5ff";
        }}
      >
        ← Voltar
      </button>

      {/* Logo */}
      <div className="logo" style={{ marginBottom: "1rem" }}>YouTube Playground</div>
      <div className="subtitle" style={{ marginBottom: "2rem" }}>Transcrição e Sumarização</div>

      {/* Error Banner */}
      {error && (
        <div
          style={{
            backgroundColor: "rgba(220, 38, 38, 0.2)",
            border: "1px solid #dc2626",
            padding: "1rem",
            borderRadius: "4px",
            marginBottom: "1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ color: "#ffffff", fontSize: "0.875rem" }}>{error}</span>
          <button
            onClick={clearError}
            style={{
              background: "none",
              border: "none",
              color: "#ffffff",
              fontSize: "1.5rem",
              cursor: "pointer",
              padding: "0 0.5rem",
            }}
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
          gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
          gap: "1.5rem",
          marginBottom: "1.5rem"
        }}>
          {/* Video Player */}
          <div className="prompt-container">
            <h2 style={{
              color: "#00e5ff",
              fontSize: "1.25rem",
              marginBottom: "1rem",
              fontWeight: "700"
            }}>
              Vídeo
            </h2>
            <div
              style={{
                position: "relative",
                width: "100%",
                paddingBottom: "56.25%",
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
          <div className="prompt-container">
            {!summary ? (
              <TranscriptionView
                transcript={transcript}
                segments={segments}
                onSummarize={handleSummarize}
                onTimestampClick={handleTimestampClick}
                loading={loading}
              />
            ) : (
              <>
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
                    Resumo
                  </h2>
                  <button
                    onClick={() => resetSummary()}
                    style={{
                      padding: "0.5rem 1rem",
                      background: "rgba(255, 255, 255, 0.1)",
                      border: "1px solid rgba(255, 255, 255, 0.2)",
                      borderRadius: "4px",
                      color: "#fff",
                      cursor: "pointer",
                      fontSize: "0.875rem"
                    }}
                  >
                    Ver Transcrição
                  </button>
                </div>
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
              </>
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
    </div>
  );
};

export default PlaygroundPage;
