import React, { useState, useEffect } from 'react';
import Dashboard from './Dashboard';

const AdminAccess: React.FC = () => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [keySequence, setKeySequence] = useState<string[]>([]);

  useEffect(() => {
    // Sequência secreta: Ctrl + Alt + A + D
    const secretSequence = ['Control', 'Alt', 'KeyA', 'KeyD'];

    const handleKeyDown = (e: KeyboardEvent) => {
      const newSequence = [...keySequence, e.code];
      
      // Manter apenas as últimas 4 teclas
      if (newSequence.length > 4) {
        newSequence.shift();
      }
      
      setKeySequence(newSequence);

      // Verificar se a sequência está correta
      if (newSequence.length === 4) {
        const isCorrect = newSequence.every((key, index) => key === secretSequence[index]);
        if (isCorrect) {
          // Acesso direto com sequência correta
          setIsAdmin(true);
          localStorage.setItem('admin-session', 'active');
          setKeySequence([]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [keySequence]);

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

  const handleLogout = () => {
    setIsAdmin(false);
    localStorage.removeItem('admin-session');
    setKeySequence([]);
  };

  if (!isAdmin) {
    return null; // Não renderiza nada se não for admin
  }

  return (
    <div className="admin-dashboard-container">
      <div className="admin-header">
        <div className="admin-info">
          <span className="admin-badge">🔒 ADMIN</span>
          <span className="admin-status">Sessão Ativa</span>
        </div>
        <button 
          onClick={handleLogout}
          className="admin-logout-btn"
        >
          🚪 Sair
        </button>
      </div>
      <Dashboard />
    </div>
  );
};

export default AdminAccess; 