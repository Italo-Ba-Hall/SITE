import React, { Suspense, lazy } from 'react';
import './App.css';
import BackgroundCanvas from './components/BackgroundCanvas';
import AnimationIntro from './components/AnimationIntro';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './components/Toast';
import LoadingSpinner from './components/LoadingSpinner';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Lazy loading para componentes pesados
const MainContent = lazy(() => import('./components/MainContent'));
const AdminAccess = lazy(() => import('./components/AdminAccess'));

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <div className="App">
            <BackgroundCanvas />
            <AnimationIntro />
            <Suspense fallback={
              <div className="flex items-center justify-center min-h-screen">
                <LoadingSpinner size="large" color="cyan" text="Carregando..." />
              </div>
            }>
              <Routes>
                <Route path="/" element={<MainContent />} />
              </Routes>
              {/* Acesso administrativo secreto - não aparece na navegação */}
              <AdminAccess />
            </Suspense>
          </div>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
