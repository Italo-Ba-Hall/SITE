import React, { useState, useMemo } from 'react';
import './SummaryView.css';

interface SummarySection {
  title: string;
  content: string;
}

interface Summary {
  summary: string;
  key_points: string[];
  keywords_found?: string[] | null;
  sections?: SummarySection[] | null;
  confidence: number;
  was_truncated: boolean;
}

interface SummaryViewProps {
  summary: Summary;
  onExport?: (format: 'txt' | 'pdf') => void;
}

const SummaryView: React.FC<SummaryViewProps> = ({ summary, onExport }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const highlightText = (text: string, term: string): React.ReactNode => {
    if (!term.trim()) return text;

    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} style={{ backgroundColor: 'rgba(0, 212, 255, 0.3)', padding: '0 2px' }}>
          {part}
        </mark>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  const matchCount = useMemo(() => {
    if (!searchTerm.trim()) return 0;

    const allText = [
      summary.summary,
      ...summary.key_points,
      ...(summary.sections?.map(s => s.title + ' ' + s.content) || [])
    ].join(' ');

    const matches = allText.match(new RegExp(searchTerm, 'gi'));
    return matches ? matches.length : 0;
  }, [searchTerm, summary]);

  return (
    <div className="summary-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 className="summary-title" style={{ marginBottom: 0 }}>Resumo Inteligente</h2>
        {onExport && (
          <button
            onClick={() => onExport('txt')}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(100, 200, 100, 0.3)',
              border: '1px solid rgba(100, 200, 100, 0.7)',
              borderRadius: '6px',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '0.9rem',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(100, 200, 100, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(100, 200, 100, 0.3)';
            }}
          >
            Exportar TXT
          </button>
        )}
      </div>

      {/* Campo de Busca */}
      <div className="search-container" style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Buscar no resumo..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '0.6rem 1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '6px',
            color: '#fff',
            fontSize: '0.9rem',
          }}
        />
        {searchTerm && (
          <div style={{ 
            marginTop: '0.5rem', 
            fontSize: '0.85rem', 
            color: 'rgba(255, 255, 255, 0.6)' 
          }}>
            {matchCount} resultado(s) encontrado(s)
          </div>
        )}
      </div>

      <div className="summary-confidence">
        Confiança: {(summary.confidence * 100).toFixed(0)}%
      </div>

      <div className="summary-section">
        <h3>Resumo Geral</h3>
        <p className="summary-text">{highlightText(summary.summary, searchTerm)}</p>
      </div>

      {summary.key_points && summary.key_points.length > 0 && (
        <div className="summary-section">
          <h3>Pontos Principais</h3>
          <ul className="key-points-list">
            {summary.key_points.map((point, index) => (
              <li key={index} className="key-point-item">
                {highlightText(point, searchTerm)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary.keywords_found && summary.keywords_found.length > 0 && (
        <div className="summary-section">
          <h3>Palavras-chave Encontradas</h3>
          <div className="keywords-container">
            {summary.keywords_found.map((keyword, index) => (
              <span key={index} className="keyword-tag">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {summary.sections && summary.sections.length > 0 && (
        <div className="summary-section">
          <h3>Seções Temáticas</h3>
          {summary.sections.map((section, index) => (
            <div key={index} className="thematic-section">
              <h4 className="section-title">{highlightText(section.title, searchTerm)}</h4>
              <p className="section-content">{highlightText(section.content, searchTerm)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SummaryView;
