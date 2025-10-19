import React, { useState, useMemo } from 'react';
import './TranscriptionView.css';

interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
  end: number;
}

interface TranscriptionViewProps {
  transcript: string | null;
  segments?: TranscriptSegment[];
  onSummarize: (context?: string, keywords?: string[]) => void;
  onTimestampClick?: (timestamp: number) => void;
  loading?: boolean;
}

const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  transcript,
  segments = [],
  onSummarize,
  onTimestampClick,
  loading = false,
}) => {
  const [context, setContext] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');
  const [showSummarizeForm, setShowSummarizeForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSummarize = () => {
    const keywords = keywordsInput
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    onSummarize(context || undefined, keywords.length > 0 ? keywords : undefined);
    setShowSummarizeForm(false);
  };

  const formatTimestamp = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleTimestampClick = (timestamp: number) => {
    if (onTimestampClick) {
      onTimestampClick(timestamp);
    }
  };

  // Filtrar segments com base na busca
  const filteredSegments = useMemo(() => {
    if (!searchQuery || segments.length === 0) {
      return segments;
    }

    return segments.filter(segment =>
      segment.text.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [segments, searchQuery]);

  // Highlight do texto de busca
  const highlightText = (text: string, query: string): React.ReactNode => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={index} className="highlight">{part}</mark>
      ) : (
        part
      )
    );
  };

  if (!transcript) {
    return (
      <div className="transcription-placeholder">
        <p>A transcrição aparecerá aqui após você inserir uma URL válida</p>
      </div>
    );
  }

  return (
    <div className="transcription-view">
      <div className="transcription-header">
        <h2>Transcrição</h2>
        <div className="header-actions">
          {segments.length > 0 && (
            <input
              type="text"
              placeholder="Buscar na transcrição..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          )}
          <button
            className="summarize-toggle-button"
            onClick={() => setShowSummarizeForm(!showSummarizeForm)}
            disabled={loading}
          >
            {showSummarizeForm ? 'Ocultar' : 'Sumarizar'}
          </button>
        </div>
      </div>

      {showSummarizeForm && (
        <div className="summarize-form">
          <div className="form-group">
            <label htmlFor="context">Contexto (opcional)</label>
            <input
              id="context"
              type="text"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Ex: Foque em aspectos técnicos"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="keywords">Palavras-chave (separadas por vírgula)</label>
            <input
              id="keywords"
              type="text"
              value={keywordsInput}
              onChange={(e) => setKeywordsInput(e.target.value)}
              placeholder="Ex: tecnologia, inovação, futuro"
              className="form-input"
            />
          </div>

          <button
            className="summarize-button"
            onClick={handleSummarize}
            disabled={loading}
          >
            {loading ? 'Gerando resumo...' : 'Gerar Resumo'}
          </button>
        </div>
      )}

      <div className="transcription-content">
        {segments.length > 0 ? (
          <>
            {filteredSegments.length === 0 && searchQuery && (
              <p className="no-results">Nenhum resultado encontrado para "{searchQuery}"</p>
            )}
            {filteredSegments.map((segment, index) => (
              <div key={index} className="transcript-segment">
                <button
                  className="timestamp-button"
                  onClick={() => handleTimestampClick(segment.start)}
                  title="Pular para este momento no vídeo"
                >
                  {formatTimestamp(segment.start)}
                </button>
                <span className="segment-text">
                  {highlightText(segment.text, searchQuery)}
                </span>
              </div>
            ))}
          </>
        ) : (
          <pre className="transcription-text">{transcript}</pre>
        )}
      </div>
    </div>
  );
};

export default TranscriptionView;
