import React, { useState, useEffect, useRef } from 'react';
import { useSuggestions } from '../hooks/useApi';
import SuggestionsDropdown from './SuggestionsDropdown';

interface Suggestion {
  id: string;
  title: string;
  description: string;
  category: string;
}

const MainContent: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const { suggestions, loading: suggestionsLoading, error: suggestionsError } = useSuggestions(inputValue);

  useEffect(() => {
    const handleShowMainContent = () => {
      setIsVisible(true);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 2000);
    };

    window.addEventListener('showMainContent', handleShowMainContent);

    return () => {
      window.removeEventListener('showMainContent', handleShowMainContent);
    };
  }, []);

  useEffect(() => {
    setShowSuggestions(inputValue.trim().length > 0 && !suggestionsLoading);
  }, [inputValue, suggestionsLoading]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleUnifiedInput();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setInputValue('');
    }
  };

  const handleUnifiedInput = async () => {
    const userInput = inputValue.trim();
    if (!userInput) return;

    setInputValue('');
    setShowSuggestions(false);
    // API call would be handled by useSuggestions hook
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setInputValue('');
    setShowSuggestions(false);

    const event = new CustomEvent('openModal', {
      detail: { suggestionId: suggestion.id }
    });
    window.dispatchEvent(event);
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false);
  };

  const handlePromptClick = () => {
    inputRef.current?.focus();
  };

  return (
    <div id="mainContent" className={`content ${isVisible ? 'visible' : ''}`}>
      <div className="logo">/-HALL-DEV</div>
      <div className="subtitle">Development &amp; Innovation</div>
      <div id="interfaceContainer">
        <div className="prompt-container" onClick={handlePromptClick}>
          <div className="prompt-line">
            <span className="prompt-prefix">/-HALL-DEV&gt;</span>
            <span id="promptText" className="prompt-text">{inputValue}</span>
            <span className="prompt-cursor"></span>
          </div>
          <input
            ref={inputRef}
            type="text"
            id="unifiedInput"
            className="actual-input"
            value={inputValue}
            onChange={handleInputChange}
            onKeyUp={handleKeyUp}
            placeholder=""
          />
        </div>

        {/* Error display */}
        {suggestionsError && (
          <div className="error-message text-red-400 text-sm mt-2 text-center">
            {suggestionsError || 'Erro ao carregar sugestões'}
          </div>
        )}

        {/* Suggestions Dropdown */}
        <SuggestionsDropdown
          isVisible={showSuggestions}
          suggestions={suggestions}
          isLoading={suggestionsLoading}
          onSuggestionClick={handleSuggestionClick}
          onClose={handleCloseSuggestions}
        />
      </div>
    </div>
  );
};

export default MainContent; 