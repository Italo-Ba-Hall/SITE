import React, { useState } from 'react';
import './URLInput.css';

interface URLInputProps {
  onSubmit: (url: string) => void;
  disabled?: boolean;
}

const URLInput: React.FC<URLInputProps> = ({ onSubmit, disabled = false }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="url-input-form">
      <div className="url-input-container">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Cole a URL do vídeo do YouTube aqui..."
          className="url-input"
          disabled={disabled}
        />
        <button
          type="submit"
          className="url-submit-button"
          disabled={disabled || !url.trim()}
        >
          {disabled ? 'Processando...' : 'Transcrever'}
        </button>
      </div>
      <p className="url-input-hint">
        Exemplo: https://www.youtube.com/watch?v=dQw4w9WgXcQ
      </p>
    </form>
  );
};

export default URLInput;
