import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import usePlayground from "../hooks/usePlayground";
import YouTube from "react-youtube";

const PlaygroundPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    videoId,
    transcript,
    summary,
    loading,
    error,
    handleUrlSubmit,
    handleSummarize,
    clearError,
  } = usePlayground();

  const [urlInput, setUrlInput] = useState("");
  const [showSummarizeForm, setShowSummarizeForm] = useState(false);
  const [context, setContext] = useState("");
  const [keywordsInput, setKeywordsInput] = useState("");

  const handleTranscribe = () => {
    if (urlInput.trim()) {
      handleUrlSubmit(urlInput.trim());
    }
  };

  const handleSummarizeClick = () => {
    const keywords = keywordsInput
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    handleSummarize(
      context || undefined,
      keywords.length > 0 ? keywords : undefined,
    );
  };

  // Formatar transcrição para melhor legibilidade
  const formatTranscript = (text: string) => {
    if (!text) return text;

    // Dividir em sentenças (aproximadamente) e criar parágrafos
    // Quebrar a cada 3-4 sentenças para criar parágrafos
    const sentences = text.split(/(?<=[.!?])\s+/);
    const paragraphs: string[] = [];

    for (let i = 0; i < sentences.length; i += 3) {
      const paragraph = sentences.slice(i, i + 3).join(" ");
      if (paragraph.trim()) {
        paragraphs.push(paragraph.trim());
      }
    }

    return paragraphs.join("\n\n");
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

      {/* Video Player and Transcription */}
      {videoId && !loading && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem", marginBottom: "1.5rem" }}>
          {/* Video Player */}
          <div className="prompt-container">
            <h2 style={{ color: "#00e5ff", fontSize: "1.25rem", marginBottom: "1rem", fontWeight: "700" }}>
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
                />
              </div>
            </div>
          </div>

          {/* Transcription */}
          <div className="prompt-container">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h2 style={{ color: "#00e5ff", fontSize: "1.25rem", fontWeight: "700" }}>
                Transcrição
              </h2>
              <button
                onClick={() => setShowSummarizeForm(!showSummarizeForm)}
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
                {showSummarizeForm ? "Ocultar" : "Sumarizar"}
              </button>
            </div>

            {/* Summarize Form */}
            {showSummarizeForm && (
              <div
                style={{
                  marginBottom: "1rem",
                  padding: "1rem",
                  backgroundColor: "rgba(0, 0, 0, 0.5)",
                  borderRadius: "4px",
                  border: "1px solid #1a1a1a",
                }}
              >
                <div style={{ marginBottom: "0.75rem" }}>
                  <label style={{ display: "block", color: "#cccccc", fontSize: "0.75rem", marginBottom: "0.5rem" }}>
                    Contexto
                  </label>
                  <input
                    type="text"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Ex: aspectos técnicos"
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "rgba(0, 0, 0, 0.5)",
                      border: "1px solid #1a1a1a",
                      borderRadius: "4px",
                      color: "#ffffff",
                      fontSize: "0.875rem",
                      fontFamily: "'Roboto Mono', monospace",
                      outline: "none",
                    }}
                  />
                </div>
                <div style={{ marginBottom: "0.75rem" }}>
                  <label style={{ display: "block", color: "#cccccc", fontSize: "0.75rem", marginBottom: "0.5rem" }}>
                    Palavras-chave
                  </label>
                  <input
                    type="text"
                    value={keywordsInput}
                    onChange={(e) => setKeywordsInput(e.target.value)}
                    placeholder="Ex: tecnologia, inovação"
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "rgba(0, 0, 0, 0.5)",
                      border: "1px solid #1a1a1a",
                      borderRadius: "4px",
                      color: "#ffffff",
                      fontSize: "0.875rem",
                      fontFamily: "'Roboto Mono', monospace",
                      outline: "none",
                    }}
                  />
                </div>
                <button
                  onClick={handleSummarizeClick}
                  disabled={loading}
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    background: loading ? "rgba(0, 229, 255, 0.3)" : "transparent",
                    border: "1px solid #00e5ff",
                    color: "#00e5ff",
                    borderRadius: "4px",
                    cursor: loading ? "not-allowed" : "pointer",
                    fontSize: "0.875rem",
                    fontFamily: "'Roboto Mono', monospace",
                    transition: "all 0.3s",
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) e.currentTarget.style.backgroundColor = "rgba(0, 229, 255, 0.1)";
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) e.currentTarget.style.backgroundColor = "transparent";
                  }}
                >
                  {loading ? "Gerando..." : "Gerar Resumo"}
                </button>
              </div>
            )}

            {/* Transcript Content */}
            <div
              style={{
                maxHeight: "400px",
                overflowY: "auto",
                backgroundColor: "rgba(0, 0, 0, 0.5)",
                borderRadius: "4px",
                padding: "1.5rem",
                border: "1px solid #1a1a1a",
              }}
            >
              {transcript ? (
                <div style={{
                  color: "#cccccc",
                  fontSize: "0.875rem",
                  lineHeight: "1.8",
                  whiteSpace: "pre-wrap",
                  letterSpacing: "0.02em"
                }}>
                  {formatTranscript(transcript)}
                </div>
              ) : (
                <div style={{ color: "#666666", textAlign: "center", padding: "2rem 0", fontSize: "0.875rem" }}>
                  Aguardando transcrição...
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Summary Section */}
      {summary && (
        <div className="prompt-container" style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ color: "#00e5ff", fontSize: "1.5rem", fontWeight: "700", marginBottom: "1rem" }}>
            Resumo
          </h2>

          {/* Confidence Badge */}
          <div style={{ marginBottom: "1rem" }}>
            <span
              style={{
                display: "inline-block",
                padding: "0.5rem 1rem",
                backgroundColor: "rgba(0, 229, 255, 0.2)",
                border: "1px solid #00e5ff",
                borderRadius: "20px",
                color: "#00e5ff",
                fontSize: "0.875rem",
                fontWeight: "600",
              }}
            >
              Confiança: {(summary.confidence * 100).toFixed(0)}%
            </span>
          </div>

          {/* General Summary */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ color: "#00e5ff", fontSize: "1rem", fontWeight: "700", marginBottom: "0.75rem" }}>
              Resumo Geral
            </h3>
            <p style={{ color: "#cccccc", fontSize: "0.875rem", lineHeight: "1.6" }}>
              {summary.summary}
            </p>
          </div>

          {/* Key Points */}
          {summary.key_points && summary.key_points.length > 0 && (
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ color: "#00e5ff", fontSize: "1rem", fontWeight: "700", marginBottom: "0.75rem" }}>
                Pontos Principais
              </h3>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {summary.key_points.map((point, idx) => (
                  <li
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      backgroundColor: "rgba(0, 0, 0, 0.5)",
                      padding: "0.75rem",
                      borderRadius: "4px",
                      border: "1px solid #1a1a1a",
                      marginBottom: "0.5rem",
                    }}
                  >
                    <span style={{ color: "#00e5ff", fontWeight: "700", marginRight: "0.75rem", fontSize: "0.875rem" }}>
                      {idx + 1}.
                    </span>
                    <span style={{ color: "#cccccc", fontSize: "0.875rem", lineHeight: "1.6" }}>
                      {point}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Keywords Found */}
          {summary.keywords_found && summary.keywords_found.length > 0 && (
            <div>
              <h3 style={{ color: "#00e5ff", fontSize: "1rem", fontWeight: "700", marginBottom: "0.75rem" }}>
                Palavras-chave Encontradas
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {summary.keywords_found.map((kw, idx) => (
                  <span
                    key={idx}
                    style={{
                      padding: "0.5rem 1rem",
                      backgroundColor: "rgba(59, 130, 246, 0.2)",
                      border: "1px solid #3b82f6",
                      borderRadius: "20px",
                      color: "#60a5fa",
                      fontSize: "0.75rem",
                      fontWeight: "600",
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
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
