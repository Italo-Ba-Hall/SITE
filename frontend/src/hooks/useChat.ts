import { useState, useCallback, useRef, useEffect } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatSession {
  sessionId: string;
  messages: ChatMessage[];
  isActive: boolean;
}

interface UseChatReturn {
  session: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  startChat: (initialMessage?: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  endChat: () => Promise<void>;
  isFirstInteraction: boolean;
  retryLastMessage: () => Promise<void>;
  clearError: () => void;
  isSessionReady: boolean;
  inactivityWarning: string | null;
  sessionExpired: boolean;
  saveConversation: (email: string) => Promise<boolean>;
  sendConversationEmail: (email: string) => Promise<boolean>;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configurações de retry
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 segundo
  backoffMultiplier: 2
};

// Configurações de timeout
const TIMEOUT_CONFIG = {
  warningInterval: 10 * 60 * 1000, // 10 minutos
  sessionTimeout: 15 * 60 * 1000, // 15 minutos
  checkInterval: 30 * 1000, // Verificar a cada 30 segundos
};

// Função para delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Função para fazer requisição com retry
const fetchWithRetry = async (
  url: string, 
  options: RequestInit, 
  maxRetries: number = RETRY_CONFIG.maxRetries
): Promise<Response> => {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      // Se a resposta não for ok, mas não for erro de rede, não retry
      if (!response.ok && response.status >= 400 && response.status < 500) {
        return response;
      }
      
      // Se ok ou erro 5xx, retry
      if (response.ok || response.status >= 500) {
        return response;
      }
      
    } catch (error) {
      lastError = error as Error;
      
      // Se não for o último attempt, esperar antes de tentar novamente
      if (attempt < maxRetries) {
        const waitTime = RETRY_CONFIG.retryDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, attempt);
        await delay(waitTime);
      }
    }
  }
  
  if (lastError) {
    throw lastError;
  }
  
  throw new Error('Falha na requisição após todas as tentativas');
};

export const useChat = (): UseChatReturn => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFirstInteraction, setIsFirstInteraction] = useState(true);
  const [isSessionReady, setIsSessionReady] = useState(false);
  const [inactivityWarning, setInactivityWarning] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  
  const sessionRef = useRef<string | null>(null);
  const lastMessageRef = useRef<string>('');
  const lastActivityRef = useRef<number>(Date.now());
  const timeoutIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const warningShownRef = useRef<boolean>(false);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const startChat = useCallback(async (initialMessage?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      setIsSessionReady(false);
      setSessionExpired(false);
      setInactivityWarning(null);
      warningShownRef.current = false;
      lastActivityRef.current = Date.now();

      const response = await fetchWithRetry(`${API_BASE_URL}/chat/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...(initialMessage && { initial_message: initialMessage }),
          user_id: null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      const newSession: ChatSession = {
        sessionId: data.session_id,
        messages: [],
        isActive: true
      };

      // Adicionar mensagem de boas-vindas
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: data.welcome_message,
        timestamp: new Date()
      };

      setSession(newSession);
      setMessages([welcomeMessage]);
      sessionRef.current = data.session_id;
      setIsFirstInteraction(false);
      setIsSessionReady(true);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao iniciar chat: ${errorMessage}`);
      setIsSessionReady(false);
      
      // Fallback: adicionar mensagem de erro amigável
      const fallbackMessage: ChatMessage = {
        role: 'assistant',
        content: 'Desculpe, estou com dificuldades técnicas no momento. Pode tentar novamente em alguns instantes?',
        timestamp: new Date()
      };
      
      setMessages([fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    // Verificar se a sessão está pronta
    if (!isSessionReady || !sessionRef.current) {
      setError('Aguarde a inicialização do chat...');
      return;
    }

    // Verificar se sessão expirou
    if (sessionExpired) {
      setError('Sessão expirada. Iniciando nova conversa...');
      await startChat();
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      lastMessageRef.current = message;
      lastActivityRef.current = Date.now();
      
      // Limpar avisos de inatividade quando usuário responde
      setInactivityWarning(null);
      warningShownRef.current = false;

      // Adicionar mensagem do usuário imediatamente
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);

      // Enviar para o backend
      const response = await fetchWithRetry(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionRef.current,
          message: message,
          context: null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Adicionar resposta do assistente
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao enviar mensagem: ${errorMessage}`);
      
      // Adicionar mensagem de erro amigável
      const errorMessageObj: ChatMessage = {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Pode tentar novamente?',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  }, [isSessionReady, sessionExpired, startChat]);

  const retryLastMessage = useCallback(async () => {
    if (lastMessageRef.current) {
      // Remover última mensagem de erro se existir
      setMessages(prev => {
        const filtered = prev.filter(msg => 
          !(msg.role === 'assistant' && msg.content.includes('Desculpe, ocorreu um erro'))
        );
        return filtered;
      });
      
      // Tentar enviar novamente
      await sendMessage(lastMessageRef.current);
    }
  }, [sendMessage]);

  const endChat = useCallback(async () => {
    if (!sessionRef.current) {
      return;
    }

    try {
      await fetchWithRetry(`${API_BASE_URL}/chat/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionRef.current,
          reason: 'user_ended'
        }),
      });

      // Resetar estado
      setSession(null);
      setMessages([]);
      sessionRef.current = null;
      setIsFirstInteraction(true);
      setIsSessionReady(false);
      setSessionExpired(false);
      setInactivityWarning(null);
      warningShownRef.current = false;
      lastMessageRef.current = '';

      // Limpar intervalo
      if (timeoutIntervalRef.current) {
        clearInterval(timeoutIntervalRef.current);
        timeoutIntervalRef.current = null;
      }

    } catch (err) {
      // Log do erro mas não mostrar para o usuário
      // console.error('Erro ao finalizar chat:', err);
    }
  }, []);

  // Função para verificar inatividade (movida para depois das outras funções)
  const checkInactivity = useCallback(async () => {
    if (!sessionRef.current || sessionExpired) {
      return;
    }

    try {
      const response = await fetchWithRetry(
        `${API_BASE_URL}/chat/inactivity-check/${sessionRef.current}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        
        if (data.should_warn && data.warning_message && !warningShownRef.current) {
          setInactivityWarning(data.warning_message);
          warningShownRef.current = true;
          
          // Adicionar aviso como mensagem do sistema
          const warningMessage: ChatMessage = {
            role: 'assistant',
            content: data.warning_message,
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, warningMessage]);
        }
      } else if (response.status === 404) {
        // Sessão expirada
        setSessionExpired(true);
        setInactivityWarning('Sessão expirada. Iniciando nova conversa...');
        
        // Finalizar sessão atual e iniciar nova
        await endChat();
        await startChat();
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Erro ao verificar inatividade:', err);
    }
  }, [sessionExpired, endChat, startChat]);

  // Configurar intervalo de verificação de inatividade
  useEffect(() => {
    if (isSessionReady && sessionRef.current) {
      timeoutIntervalRef.current = setInterval(checkInactivity, TIMEOUT_CONFIG.checkInterval);
      
      return () => {
        if (timeoutIntervalRef.current) {
          clearInterval(timeoutIntervalRef.current);
        }
      };
    }
  }, [isSessionReady, checkInactivity]);

  // Limpar intervalos quando componente desmontar
  useEffect(() => {
    return () => {
      if (timeoutIntervalRef.current) {
        clearInterval(timeoutIntervalRef.current);
      }
    };
  }, []);

  const saveConversation = useCallback(async (email: string): Promise<boolean> => {
    if (!sessionRef.current) {
      setError('Nenhuma sessão ativa para salvar');
      return false;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetchWithRetry(`${API_BASE_URL}/chat/save-conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionRef.current,
          email: email
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.success || false;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao salvar conversa: ${errorMessage}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendConversationEmail = useCallback(async (email: string): Promise<boolean> => {
    if (!sessionRef.current) {
      setError('Nenhuma sessão ativa para enviar');
      return false;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetchWithRetry(`${API_BASE_URL}/chat/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionRef.current,
          email: email
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.success || false;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao enviar email: ${errorMessage}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    session,
    messages,
    isLoading,
    error,
    startChat,
    sendMessage,
    endChat,
    isFirstInteraction,
    retryLastMessage,
    clearError,
    isSessionReady,
    inactivityWarning,
    sessionExpired,
    saveConversation,
    sendConversationEmail
  };
}; 