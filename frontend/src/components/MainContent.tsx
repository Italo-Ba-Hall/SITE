import React, { useState, useEffect, useRef } from 'react';

const MainContent: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleShowMainContent = () => {
      setIsVisible(true);
      // Focar no input após a animação
      setTimeout(() => {
        inputRef.current?.focus();
      }, 2000);
    };

    window.addEventListener('showMainContent', handleShowMainContent);

    return () => {
      window.removeEventListener('showMainContent', handleShowMainContent);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleUnifiedInput();
    }
  };

  const handleUnifiedInput = async () => {
    const userInput = inputValue.trim();
    if (!userInput) return;
    
    setInputValue('');
    console.log(`Chamando API para: ${userInput}`);
    // TODO: Implementar chamada para API
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
      </div>
    </div>
  );
};

export default MainContent; 