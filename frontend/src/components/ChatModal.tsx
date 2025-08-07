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
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [emailValue, setEmailValue] = useState('');
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
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
    isSessionReady,
    inactivityWarning,
    sessionExpired,
    saveConversation,
    sendConversationEmail
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

  // Efeito para mostrar aviso de inatividade
  useEffect(() => {
    if (inactivityWarning) {
      // Scroll para o final para mostrar o aviso
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [inactivityWarning]);

  // Efeito para lidar com sessão expirada
  useEffect(() => {
    if (sessionExpired) {
      // Mostrar notificação de sessão expirada
      setTimeout(() => {
        clearError();
      }, 3000);
    }
  }, [sessionExpired, clearError]);

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

  const handleSaveConversation = () => {
    setShowEmailForm(true);
  };

  const handleSendEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailValue.trim() || isSendingEmail) return;

    setIsSendingEmail(true);
    try {
      // Usar a função do hook para enviar email
      const success = await sendConversationEmail(emailValue);
      
      if (success) {
        setEmailSent(true);
        setTimeout(() => {
          setShowEmailForm(false);
          setEmailValue('');
          setEmailSent(false);
        }, 3000);
      } else {
        // Mostrar erro se falhar
        console.error('Falha ao enviar email');
      }
    } catch (error) {
      console.error('Erro ao enviar email:', error);
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleCancelEmail = () => {
    setShowEmailForm(false);
    setEmailValue('');
    setEmailSent(false);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatAssistantMessage = (content: string) => {
    // Garantir que quebras de linha sejam respeitadas
    return content
      .split('\n')
      .map((line, index) => (
        <React.Fragment key={index}>
          {line}
          {index < content.split('\n').length - 1 && <br />}
        </React.Fragment>
      ));
  };

  // Função para determinar se uma mensagem é um aviso de inatividade
  const isInactivityWarning = (content: string) => {
    return content.includes('⚠️') && content.includes('inativo');
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
        className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full flex flex-col backdrop-blur-sm"
        style={{ 
          backgroundColor: '#111827', 
          border: '1px solid #374151', 
          borderRadius: '1rem', 
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', 
          maxWidth: '90vw',
          width: '100%', 
          maxHeight: '90vh', 
          minHeight: '600px',
          display: 'flex', 
          flexDirection: 'column' 
        }}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 rounded-t-2xl sticky top-0 z-10">
          <div className="flex items-center space-x-4">
            <div className={`w-3 h-3 rounded-full ${
              sessionExpired ? 'bg-red-400 animate-pulse' : 
              isSessionReady ? 'bg-cyan-400 animate-pulse' : 'bg-yellow-400 animate-pulse'
            }`}></div>
            <div>
              <h2 className="text-cyan-400 text-xl font-bold">
                /-HALL-DEV Assistant
              </h2>
              <p className="text-gray-400 text-sm">
                {sessionExpired ? 'Sessão expirada' : 
                 isSessionReady ? 'Pronto para conversar' : 'Inicializando...'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {messages.length > 0 && (
              <button
                onClick={handleSaveConversation}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center space-x-2"
              >
                <span>📧</span>
                <span>Salvar Conversa</span>
              </button>
            )}
            <div className="text-xs text-gray-500">
              {messages.length > 0 && `${messages.length} mensagens`}
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-cyan-400 text-3xl font-bold transition-colors duration-200"
              aria-label="Fechar chat"
            >
              ×
            </button>
          </div>
        </div>

        {/* Email Form Modal */}
        {showEmailForm && (
          <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-[10000] p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
              <h3 className="text-cyan-400 text-xl font-bold mb-4">Salvar Conversa</h3>
              <p className="text-gray-400 text-sm mb-6">
                Digite seu email para receber um resumo desta conversa:
              </p>
              
              {emailSent ? (
                <div className="text-center py-8">
                  <div className="text-green-400 text-4xl mb-4">✅</div>
                  <p className="text-green-400 font-medium">Email enviado com sucesso!</p>
                  <p className="text-gray-400 text-sm mt-2">Verifique sua caixa de entrada</p>
                </div>
              ) : (
                <form onSubmit={handleSendEmail} className="space-y-4">
                  <input
                    type="email"
                    value={emailValue}
                    onChange={(e) => setEmailValue(e.target.value)}
                    placeholder="seu@email.com"
                    required
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400"
                  />
                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      disabled={!emailValue.trim() || isSendingEmail}
                      className="flex-1 bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white px-4 py-3 rounded-lg font-medium transition-colors duration-200"
                    >
                      {isSendingEmail ? 'Enviando...' : 'Enviar'}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelEmail}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg font-medium transition-colors duration-200"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Messages Container */}
        <div 
          className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-900 messages-container" 
          style={{ 
            maxHeight: 'calc(90vh - 200px)', 
            minHeight: '400px',
            overflowY: 'auto',
            scrollbarWidth: 'thin',
            scrollbarColor: '#374151 #1f2937'
          }}
        >
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
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg border border-blue-400'
                      : isInactivityWarning(message.content)
                      ? 'bg-yellow-900 border-2 border-yellow-600 text-yellow-100 shadow-lg animate-pulse'
                      : 'bg-gray-800 border border-gray-700 text-cyan-400 shadow-lg'
                  }`}
                  style={{
                    ...(message.role === 'user' && {
                      background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                      border: '1px solid #60a5fa',
                      boxShadow: '0 10px 25px -5px rgba(37, 99, 235, 0.3)'
                    }),
                    ...(message.role === 'assistant' && !isInactivityWarning(message.content) && {
                      color: '#00e5ff',
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151'
                    }),
                    ...(isInactivityWarning(message.content) && {
                      backgroundColor: '#78350f',
                      border: '2px solid #d97706',
                      color: '#fef3c7'
                    })
                  }}
                >
                  <div 
                    className="whitespace-pre-wrap text-base leading-relaxed break-words"
                    style={{
                      ...(message.role === 'user' && {
                        color: '#ffffff',
                        fontWeight: '500'
                      }),
                      ...(message.role === 'assistant' && !isInactivityWarning(message.content) && {
                        color: '#00e5ff'
                      }),
                      ...(isInactivityWarning(message.content) && {
                        color: '#fef3c7'
                      })
                    }}
                  >
                    {message.role === 'assistant' 
                      ? formatAssistantMessage(message.content)
                      : message.content
                    }
                  </div>
                  <div className={`text-xs mt-3 ${
                    message.role === 'user' ? 'text-blue-200' : 
                    isInactivityWarning(message.content) ? 'text-yellow-200' : 'text-gray-500'
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
        <div className="p-6 border-t border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800 rounded-b-2xl sticky bottom-0">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                sessionExpired ? "Sessão expirada. Iniciando nova conversa..." :
                isSessionReady ? "Digite sua mensagem..." : "Inicializando chat..."
              }
              disabled={isLoading || !isSessionReady || sessionExpired}
              className="flex-1 px-6 py-4 bg-gray-800 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 disabled:opacity-50 text-base transition-all duration-200 min-w-0"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading || !isSessionReady || sessionExpired}
              className="px-8 py-4 bg-cyan-600 text-white rounded-xl hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-400 font-medium text-base whitespace-nowrap"
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