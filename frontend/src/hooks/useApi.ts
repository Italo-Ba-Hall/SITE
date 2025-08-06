import { useState, useEffect, useCallback, useRef } from 'react';

interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface ApiConfig {
  debounceMs?: number;
  cacheTimeout?: number;
}

// Cache simples para evitar requisições desnecessárias
const cache = new Map<string, { data: unknown; timestamp: number }>();

export const useApi = <T>(
  url: string,
  config: ApiConfig = {}
): ApiResponse<T> & { refetch: () => void } => {
  const { debounceMs = 500, cacheTimeout = 5 * 60 * 1000 } = config;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const debounceRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const abortControllerRef = useRef<AbortController | undefined>(undefined);

  const fetchData = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      setError(null);

      // Verificar cache
      const cached = cache.get(url);
      if (cached && Date.now() - cached.timestamp < cacheTimeout) {
        setData(cached.data as T);
        setLoading(false);
        return;
      }

      const response = await fetch(url, {
        signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Armazenar no cache
      cache.set(url, { data: result, timestamp: Date.now() });
      
      setData(result);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return; // Ignorar erros de abort
      }
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [url, cacheTimeout]);

  const debouncedFetch = useCallback(() => {
    // Cancelar requisição anterior
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo controller
    abortControllerRef.current = new AbortController();

    // Limpar debounce anterior
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Configurar novo debounce
    debounceRef.current = setTimeout(() => {
      fetchData(abortControllerRef.current?.signal);
    }, debounceMs);
  }, [fetchData, debounceMs]);

  const refetch = useCallback(() => {
    // Limpar cache para esta URL
    cache.delete(url);
    debouncedFetch();
  }, [url, debouncedFetch]);

  useEffect(() => {
    debouncedFetch();

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [debouncedFetch]);

  return { data, loading, error, refetch };
};

// Hook específico para sugestões
export const useSuggestions = (text: string) => {
  const [suggestions, setSuggestions] = useState<Array<{
    id: string;
    title: string;
    description: string;
    category: string;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const abortControllerRef = useRef<AbortController | undefined>(undefined);

  const fetchSuggestions = useCallback(async (inputText: string) => {
    if (!inputText.trim()) {
      setSuggestions([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Cancelar requisição anterior
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      const response = await fetch('http://localhost:8000/suggest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setSuggestions(result);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      setError(err instanceof Error ? err.message : 'Erro ao buscar sugestões');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      fetchSuggestions(text);
    }, 500);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [text, fetchSuggestions]);

  return { suggestions, loading, error };
};

// Hook para buscar conteúdo detalhado
export const useContent = (suggestionId: string | null) => {
  const { data, loading, error } = useApi<{
    id: string;
    title: string;
    content: string;
    details: Record<string, unknown>;
  }>(
    suggestionId ? `http://localhost:8000/content/${suggestionId}` : '',
    { debounceMs: 0, cacheTimeout: 10 * 60 * 1000 } // Cache por 10 minutos
  );

  return { content: data, loading, error };
}; 