import React from 'react';
import './App.css';
import BackgroundCanvas from './components/BackgroundCanvas';
import AnimationIntro from './components/AnimationIntro';
import MainContent from './components/MainContent';
import ResultModal from './components/ResultModal';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <div className="App" style={{backgroundColor: '#080808', minHeight: '100vh'}}>
        <Navbar />
        <BackgroundCanvas />
        <AnimationIntro />
        <MainContent />
        <ResultModal />
      </div>
    </ErrorBoundary>
  );
}

export default App;
