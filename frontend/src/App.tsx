import React, { Suspense, lazy, useMemo } from 'react';
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
const PlaygroundContainer = lazy(() => import('./components/playground/PlaygroundContainer'));

function App() {
  const isAdminMode = useMemo(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      if (params.get('admin') === 'hall-dev-secret-2024') return true;
      return localStorage.getItem('admin-session') === 'active';
    } catch {
      return false;
    }
  }, []);

  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <div className="App">
            {!isAdminMode && (
              <>
                <BackgroundCanvas />
                <AnimationIntro />
              </>
            )}
            <Suspense fallback={
              <div className="flex items-center justify-center min-h-screen">
                <LoadingSpinner size="large" color="cyan" text="Carregando..." />
              </div>
            }>
              <Routes>
                <Route path="/" element={isAdminMode ? <AdminAccess /> : <MainContent />} />
                <Route path="/playground" element={<PlaygroundContainer />} />
              </Routes>
            </Suspense>
          </div>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
