import React from 'react';

const Navbar: React.FC = () => {
  const handleDivirtaSe = () => {
    // TODO: Implementar funcionalidade "Divirta-se"
    // Por exemplo: abrir uma seção de jogos ou demos
  };

  const handleCrie = () => {
    // TODO: Implementar funcionalidade "Crie"
    // Por exemplo: abrir formulário de criação de projeto
  };

  return (
    <nav className="navbar absolute top-0 left-0 right-0 z-50 p-4">
      <div className="flex justify-end space-x-4">
        <button
          onClick={handleDivirtaSe}
          className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors duration-200"
        >
          Divirta-se
        </button>
        <button
          onClick={handleCrie}
          className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors duration-200"
        >
          Crie
        </button>
      </div>
    </nav>
  );
};

export default Navbar; 