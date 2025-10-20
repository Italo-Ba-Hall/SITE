// Configurações de performance para o projeto /-HALL-DEV

// Constantes de API
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_TIMEOUT_MS = 10000;
export const DEBOUNCE_DELAY_MS = 500;
export const CACHE_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutos

// Configurações de animação
export const ANIMATION_DURATION = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
  INTRO: 2000
};

// Configurações de cache
export const CACHE_CONFIG = {
  SUGGESTIONS: 5 * 60 * 1000, // 5 minutos
  CONTENT: 10 * 60 * 1000, // 10 minutos
  USER_DATA: 30 * 60 * 1000 // 30 minutos
};

// Configurações de monitoramento
export const MONITORING_CONFIG = {
  ERROR_SAMPLE_RATE: 0.1, // 10% dos erros
  PERFORMANCE_SAMPLE_RATE: 0.05, // 5% das métricas
  SESSION_TIMEOUT: 30 * 60 * 1000 // 30 minutos
};

// Configurações de otimização
export const OPTIMIZATION_CONFIG = {
  LAZY_LOAD_THRESHOLD: 0.1, // 10% da viewport
  IMAGE_LAZY_LOAD: true,
  COMPONENT_LAZY_LOAD: true,
  API_CACHE_ENABLED: true
};

// Configurações de mobile
export const MOBILE_CONFIG = {
  TOUCH_THRESHOLD: 10,
  SWIPE_THRESHOLD: 50,
  LONG_PRESS_DELAY: 500
};

// Configurações de conexão
export const CONNECTION_CONFIG = {
  SLOW_CONNECTION_THRESHOLD: 1000, // 1 segundo
  OFFLINE_TIMEOUT: 5000, // 5 segundos
  RETRY_ATTEMPTS: 3
};

// Funções utilitárias de performance

// Verificar se é dispositivo móvel
export const isMobile = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

// Verificar se é conexão lenta
export const isSlowConnection = (): boolean => {
  const connection = (navigator as Navigator & { connection?: { effectiveType?: string } }).connection;
  return connection?.effectiveType === 'slow-2g' ||
         connection?.effectiveType === '2g';
};

// Verificar se está offline
export const isOffline = (): boolean => {
  return !navigator.onLine;
};

// Debounce function
export const debounce = <T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Throttle function
export const throttle = <T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Memoization helper
export const memoize = <T extends (...args: unknown[]) => unknown>(
  func: T
): T => {
  const cache = new Map<string, unknown>();
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      const cached = cache.get(key);
      if (cached !== undefined) {
        return cached as ReturnType<T>;
      }
    }
    const result = func(...args);
    cache.set(key, result);
    return result as ReturnType<T>;
  }) as T;
};

// Performance monitoring
export const measurePerformance = (name: string, fn: () => void): void => {
  const start = performance.now();
  fn();
  const end = performance.now();

  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.log(`${name} took ${end - start}ms`); // Performance tracking apenas em development
  }
};

// Error tracking
export const trackError = (error: Error, context?: Record<string, unknown>): void => {
  if (process.env.NODE_ENV === 'production') {
    // TODO: Implement error tracking service
    // Example: Sentry.captureException(error, { extra: context });
  } else {
    // eslint-disable-next-line no-console
    console.error('Error tracked:', error, context); // Error tracking apenas em development
  }
};

// Memory usage monitoring
export const getMemoryUsage = (): { used: number; total: number } | null => {
  if ('memory' in performance) {
    const memory = (performance as Performance & { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
    if (memory) {
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize
      };
    }
  }
  return null;
};

// Network status monitoring
export const getNetworkInfo = (): { effectiveType?: string; downlink?: number } => {
  const connection = (navigator as Navigator & { connection?: { effectiveType?: string; downlink?: number } }).connection;
  return {
    effectiveType: connection?.effectiveType,
    downlink: connection?.downlink
  };
}; 