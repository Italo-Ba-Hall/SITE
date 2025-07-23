/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['Roboto Mono', 'monospace'],
      },
      colors: {
        'cyber-blue': '#00e5ff',
        'deep-black': '#080808',
        'card-black': '#010101',
      },
      animation: {
        'blink': 'blink 1s steps(2, start) infinite',
      },
      keyframes: {
        blink: {
          'to': { visibility: 'hidden' }
        }
      }
    },
  },
  plugins: [],
} 