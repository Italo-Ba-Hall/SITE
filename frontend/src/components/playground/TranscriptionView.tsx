import React, { useState } from 'react';
import './TranscriptionView.css';

interface TranscriptionViewProps {
  transcript: string | null;
  onSummarize: (context?: string, keywords?: string[]) => void;
  loading?: boolean;
}

const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  transcript,
  onSummarize,
  loading = false,
}) => {
  const [context, setContext] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');
  const [showSummarizeForm, setShowSummarizeForm] = useState(false);

  const handleSummarize = () => {
    const keywords = keywordsInput
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    onSummarize(context || undefined, keywords.length > 0 ? keywords : undefined);
    setShowSummarizeForm(false);
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
        <button
          className="summarize-toggle-button"
          onClick={() => setShowSummarizeForm(!showSummarizeForm)}
          disabled={loading}
        >
          {showSummarizeForm ? 'Ocultar' : 'Sumarizar'}
        </button>
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
        <pre className="transcription-text">{transcript}</pre>
      </div>
    </div>
  );
};

export default TranscriptionView;
