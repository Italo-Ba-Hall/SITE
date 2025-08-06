import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useChat } from '../hooks/useChat';

interface ChatModalProps {
  isVisible: boolean;
  initialMessage?: string;
  onClose?: () => void;
}

const ChatModal: React.FC<ChatModalProps> = ({
  isVisible,
  initialMessage,
  onClose
}) => {
  const [inputValue, setInputValue] = useState('');
  const [modalVisible, setModalVisible] = useState(isVisible);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    messages,
    isLoading,
    error,
    startChat,
    sendMessage,
    endChat,
    retryLastMessage,
    clearError,
    isSessionReady
  } = useChat();

  useEffect(() => {
    setModalVisible(isVisible);
    if (isVisible && initialMessage) {
      startChat(initialMessage);
    }
  }, [isVisible, initialMessage, startChat]);

  useEffect(() => {
    // Scroll para a última mensagem
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Focar no input quando modal abrir e sessão estiver pronta
    if (modalVisible && isSessionReady) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [modalVisible, isSessionReady]);

  const handleClose = useCallback(() => {
    setModalVisible(false);
    endChat();
    if (onClose) {
      onClose();
    }
  }, [endChat, onClose]);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const message = inputValue.trim();
    if (!message || isLoading || !isSessionReady) return;

    setInputValue('');
    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleRetry = async () => {
    clearError();
    await retryLastMessage();
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!modalVisible) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-[9999] p-4"
      style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999 }}
      onClick={handleOverlayClick}
    >
      <div 
        className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col backdrop-blur-sm"
        style={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '1rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', maxWidth: '64rem', width: '100%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
      >
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
            onClick={handleClose}
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
                  onClick={handleRetry}
                  className="text-xs bg-red-700 hover:bg-red-600 px-4 py-2 rounded-lg transition-colors duration-200 font-medium"
                >
                  Tentar Novamente
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-6 border-t border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 rounded-b-2xl">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isSessionReady ? "Digite sua mensagem..." : "Inicializando chat..."}
              disabled={isLoading || !isSessionReady}
              className="flex-1 px-6 py-4 bg-gray-800 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 disabled:opacity-50 text-base transition-all duration-200"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading || !isSessionReady}
              className="px-8 py-4 bg-cyan-600 text-white rounded-xl hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-400 font-medium text-base"
            >
              Enviar
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatModal; 