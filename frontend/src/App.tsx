import React from 'react';
import './App.css';
import MainContent from './components/MainContent';
import AdminAccess from './components/AdminAccess';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<MainContent />} />
        </Routes>
        {/* Acesso administrativo secreto - não aparece na navegação */}
        <AdminAccess />
      </div>
    </Router>
  );
}

export default App;
