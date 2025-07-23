import React from 'react';
import './App.css';
import BackgroundCanvas from './components/BackgroundCanvas';
import AnimationIntro from './components/AnimationIntro';
import MainContent from './components/MainContent';
import ResultModal from './components/ResultModal';

function App() {
  return (
    <div className="App bg-deep-black min-h-screen">
      <BackgroundCanvas />
      <AnimationIntro />
      <MainContent />
      <ResultModal />
    </div>
  );
}

export default App;
