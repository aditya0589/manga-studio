/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0b0e',
        surface: {
          DEFAULT: '#12141a',
          card: '#161922',
          hover: '#1e222e',
          active: '#262b3a',
          border: '#2a2f40'
        },
        studio: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        panel: {
          border: '#33384a',
          bg: '#0f1117',
          highlight: '#3b82f6'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        manga: ['Anime Ace', 'Impact', 'system-ui', 'sans-serif'],
        comic: ['Bangers', 'Comic Sans MS', 'cursive', 'sans-serif']
      }
    },
  },
  plugins: [],
}
