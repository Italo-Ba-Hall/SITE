import React, { useState, useEffect, useCallback } from 'react';
import Dashboard from './Dashboard';

const AdminAccess: React.FC = () => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [keySequence, setKeySequence] = useState<string[]>([]);

  const handleLogout = useCallback(() => {
    setIsAdmin(false);
    localStorage.removeItem('admin-session');
    setKeySequence([]);
  }, []);

  useEffect(() => {
    // Sequência secreta: Ctrl + Alt + A + D
    const secretSequence = ['Control', 'Alt', 'KeyA', 'KeyD'];

    const handleKeyDown = (e: KeyboardEvent) => {
      // Fechar com ESC
      if (e.key === 'Escape') {
        handleLogout();
        return;
      }

      const newSequence = [...keySequence, e.code];
      if (newSequence.length > 4) newSequence.shift();
      setKeySequence(newSequence);

      if (newSequence.length === 4) {
        const isCorrect = newSequence.every((key, index) => key === secretSequence[index]);
        if (isCorrect) {
          setIsAdmin(true);
          localStorage.setItem('admin-session', 'active');
          setKeySequence([]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [keySequence, handleLogout]);

  // Verificar se é acesso via URL especial
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const adminToken = urlParams.get('admin');
    if (adminToken === 'hall-dev-secret-2024') {
      setIsAdmin(true);
    }
  }, []);

  // Verificar se é acesso via localStorage (para persistência)
  useEffect(() => {
    const adminSession = localStorage.getItem('admin-session');
    if (adminSession === 'active') {
      setIsAdmin(true);
    }
  }, []);

  // Forçar estilo do body adequado para o dashboard admin (sem afetar público)
  useEffect(() => {
    if (!isAdmin) return;
    const prev = {
      overflow: document.body.style.overflow,
      background: document.body.style.background,
      color: document.body.style.color,
      fontFamily: document.body.style.fontFamily,
    };
    document.body.style.overflow = 'auto';
    document.body.style.background = '#f8fafc'; // cinza claro
    document.body.style.color = '#111827'; // cinza-900
    document.body.style.fontFamily = 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial';
    return () => {
      document.body.style.overflow = prev.overflow;
      document.body.style.background = prev.background;
      document.body.style.color = prev.color;
      document.body.style.fontFamily = prev.fontFamily;
    };
  }, [isAdmin]);

  if (!isAdmin) return null; // Não renderiza nada se não for admin

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 overflow-y-auto text-gray-900">
      {/* Topbar */}
      <div className="sticky top-0 z-20 backdrop-blur bg-white/80 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold bg-cyan-600 text-white">ADMIN</span>
            <span className="text-gray-700 text-sm">Sessão ativa</span>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-700 hover:text-gray-900 px-3 py-1.5 border border-gray-300 rounded-md hover:border-gray-400"
            aria-label="Sair do painel"
          >
            Sair
          </button>
        </div>
      </div>

      {/* Área principal */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <Dashboard />
      </div>
    </div>
  );
};

export default AdminAccess;