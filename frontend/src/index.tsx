import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Suprimir warnings conhecidos do YouTube iframe que não afetam a funcionalidade
// eslint-disable-next-line no-console
const originalWarn = console.warn;
// eslint-disable-next-line no-console
console.warn = (...args: unknown[]) => {
  const message = args[0]?.toString() || '';
  
  // Filtrar warnings do YouTube postMessage (são esperados devido a CORS)
  if (message.includes('postMessage') && (message.includes('youtube.com') || message.includes('www-widgetapi'))) {
    return;
  }
  
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
