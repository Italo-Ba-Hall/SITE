import React from 'react';
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
}

interface SummaryViewProps {
  summary: Summary;
}

const SummaryView: React.FC<SummaryViewProps> = ({ summary }) => {
  return (
    <div className="summary-view">
      <h2 className="summary-title">Resumo Inteligente</h2>

      <div className="summary-confidence">
        Confiança: {(summary.confidence * 100).toFixed(0)}%
      </div>

      <div className="summary-section">
        <h3>Resumo Geral</h3>
        <p className="summary-text">{summary.summary}</p>
      </div>

      {summary.key_points && summary.key_points.length > 0 && (
        <div className="summary-section">
          <h3>Pontos Principais</h3>
          <ul className="key-points-list">
            {summary.key_points.map((point, index) => (
              <li key={index} className="key-point-item">
                {point}
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
              <h4 className="section-title">{section.title}</h4>
              <p className="section-content">{section.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SummaryView;
