import React from 'react';
import URLInput from './URLInput';
import YouTubePlayer from './YouTubePlayer';
import TranscriptionView from './TranscriptionView';
import SummaryView from './SummaryView';
import usePlayground from '../../hooks/usePlayground';
import LoadingSpinner from '../LoadingSpinner';
import './PlaygroundContainer.css';

const PlaygroundContainer: React.FC = () => {
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

  return (
    <div className="playground-container">
      <div className="playground-header">
        <h1 className="playground-title">YouTube Transcription Playground</h1>
        <p className="playground-subtitle">
          Extraia transcrições de vídeos do YouTube e gere resumos inteligentes
        </p>
      </div>

      {error && (
        <div className="playground-error">
          <span>{error}</span>
          <button onClick={clearError} className="error-close">×</button>
        </div>
      )}

      <div className="playground-content">
        <URLInput onSubmit={handleUrlSubmit} disabled={loading} />

        {loading && (
          <div className="playground-loading">
            <LoadingSpinner size="large" color="cyan" text="Processando..." />
          </div>
        )}

        {videoId && (
          <div className="playground-grid">
            <div className="playground-video-section">
              <YouTubePlayer videoId={videoId} />
            </div>

            <div className="playground-transcript-section">
              <TranscriptionView
                transcript={transcript}
                onSummarize={handleSummarize}
                loading={loading}
              />
            </div>

            {summary && (
              <div className="playground-summary-section">
                <SummaryView summary={summary} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaygroundContainer;
