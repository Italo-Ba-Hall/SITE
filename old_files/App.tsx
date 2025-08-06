import React from 'react';
import './App.css';
import BackgroundCanvas from './components/BackgroundCanvas';
import AnimationIntro from './components/AnimationIntro';
import MainContent from './components/MainContent';
import ResultModal from './components/ResultModal';

function App() {
  return (
    <div className="App" style={{backgroundColor: '#080808', minHeight: '100vh'}}>
      <BackgroundCanvas />
      <AnimationIntro />
      <MainContent />
      <ResultModal />
    </div>
  );
}

export default App;
