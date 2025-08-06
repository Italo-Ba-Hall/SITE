import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';

const MainContent: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [showChatModal, setShowChatModal] = useState(false);
  const [initialMessage, setInitialMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    messages,
    isLoading,
    error,
    startChat,
    sendMessage,
    endChat,
    retryLastMessage,
    isSessionReady
  } = useChat();

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

  // Iniciar chat quando modal for aberto
  useEffect(() => {
    if (showChatModal && initialMessage) {
      startChat(initialMessage);
    }
  }, [showChatModal, initialMessage, startChat]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleUnifiedInput();
    } else if (e.key === 'Escape') {
      setInputValue('');
    }
  };

  const handleUnifiedInput = async () => {
    const userInput = inputValue.trim();
    if (!userInput) return;

    // Se não há chat ativo, iniciar um novo
    if (!showChatModal) {
      setInitialMessage(userInput);
      setShowChatModal(true);
      setInputValue('');
      return;
    }

    // Se já há chat ativo, enviar mensagem
    if (isSessionReady) {
      await sendMessage(userInput);
      setInputValue('');
    }
  };

  const handlePromptClick = () => {
    inputRef.current?.focus();
  };

  const handleCloseChat = () => {
    setShowChatModal(false);
    setInitialMessage('');
    endChat();
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
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

        {/* Chat Interface - Integrada na página principal */}
        {showChatModal && (
          <div className="chat-interface mt-6 max-w-4xl mx-auto">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl backdrop-blur-sm">
              {/* Header */}
              <div className="flex justify-between items-center p-6 border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 rounded-t-2xl">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${isSessionReady ? 'bg-cyan-400 animate-pulse' : 'bg-yellow-400 animate-pulse'}`}></div>
                  <div>
                    <h2 className="text-cyan-400 text-xl font-bold">
                      /-HALL-DEV Assistant
                    </h2>
                    <p className="text-gray-400 text-sm">
                      {isSessionReady ? 'Pronto para conversar' : 'Inicializando...'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleCloseChat}
                  className="text-gray-400 hover:text-cyan-400 text-3xl font-bold transition-colors duration-200"
                  aria-label="Fechar chat"
                >
                  ×
                </button>
              </div>

              {/* Messages Container */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 max-h-[60vh] bg-gray-900">
                {messages.length === 0 && !isLoading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
                    <p className="text-cyan-400 text-lg font-medium">Iniciando conversa...</p>
                    <p className="text-gray-400 text-sm mt-2">Preparando o assistente para você</p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl px-6 py-4 ${
                          message.role === 'user'
                            ? 'bg-cyan-600 text-white shadow-lg'
                            : 'bg-gray-800 border border-gray-700 text-cyan-400 shadow-lg'
                        }`}
                        style={{
                          ...(message.role === 'assistant' && {
                            color: '#00e5ff',
                            backgroundColor: '#1f2937',
                            border: '1px solid #374151'
                          })
                        }}
                      >
                        <div 
                          className="whitespace-pre-wrap text-base leading-relaxed"
                          style={{
                            ...(message.role === 'assistant' && {
                              color: '#00e5ff'
                            })
                          }}
                        >
                          {message.content}
                        </div>
                        <div className={`text-xs mt-3 ${
                          message.role === 'user' ? 'text-cyan-200' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
                        </div>
                      </div>
                    </div>
                  ))
                )}

                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-800 border border-gray-700 text-cyan-400 rounded-2xl px-6 py-4 shadow-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm font-medium">Digitando...</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error message with retry button */}
                {error && (
                  <div className="flex justify-start">
                    <div className="bg-red-900 border border-red-700 text-white rounded-2xl px-6 py-4 max-w-[85%] shadow-lg">
                      <div className="text-sm mb-3 font-medium">⚠️ {error}</div>
                      <button
                        onClick={retryLastMessage}
                        className="text-xs bg-red-700 hover:bg-red-600 px-4 py-2 rounded-lg transition-colors duration-200 font-medium"
                      >
                        Tentar Novamente
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MainContent; 