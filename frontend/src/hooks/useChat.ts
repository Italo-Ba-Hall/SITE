import { useState, useCallback, useRef } from 'react';

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
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configurações de retry
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 segundo
  backoffMultiplier: 2
};

// Função para delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Função para fazer requisição com retry
const fetchWithRetry = async (
  url: string, 
  options: RequestInit, 
  maxRetries: number = RETRY_CONFIG.maxRetries
): Promise<Response> => {
  let lastError: Error;
  
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
  
  throw lastError!;
};

export const useChat = (): UseChatReturn => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFirstInteraction, setIsFirstInteraction] = useState(true);
  
  const sessionRef = useRef<string | null>(null);
  const lastMessageRef = useRef<string>('');

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const startChat = useCallback(async (initialMessage?: string) => {
    try {
      setIsLoading(true);
      setError(null);

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

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao iniciar chat: ${errorMessage}`);
      
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
    if (!sessionRef.current) {
      setError('Sessão não encontrada');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      lastMessageRef.current = message;

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
  }, []);

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
      lastMessageRef.current = '';

    } catch (err) {
      // Log do erro mas não mostrar para o usuário
      console.error('Erro ao finalizar chat:', err);
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
    clearError
  };
}; 