import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders /-HALL-DEV logo', () => {
  render(<App />);
  // Usar getAllByText para encontrar todos os elementos com o texto
  const logoElements = screen.getAllByText(/-HALL-DEV/i);
  expect(logoElements.length).toBeGreaterThan(0);
});

test('renders navigation elements', () => {
  render(<App />);
  const divertaseButton = screen.getByText(/Divirta-se/i);
  const crieButton = screen.getByText(/Crie/i);
  
  expect(divertaseButton).toBeInTheDocument();
  expect(crieButton).toBeInTheDocument();
});
