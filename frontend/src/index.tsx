import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Filtro para suprimir warnings conhecidos do YouTube iframe
// Esses warnings não afetam a funcionalidade e são esperados devido às políticas de CORS do YouTube
const originalWarn = console.warn;
console.warn = (...args: unknown[]) => {
  const message = args[0]?.toString() || '';
  
  // Suprimir warnings específicos do YouTube postMessage
  if (
    message.includes('postMessage') && 
    (message.includes('youtube.com') || message.includes('www-widgetapi'))
  ) {
    return;
  }
  
  // Passar outros warnings normalmente
  originalWarn.apply(console, args);
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
