/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        episteme: {
          bg: '#090b10',
          surface: '#11161f',
          border: '#252f42',
          text: '#e7ebf3',
          subtext: '#9aa7b7',
          accent: '#6f8cff',
          success: '#6dd6a0',
          warning: '#ffbf6b',
          danger: '#ff6b7d'
        }
      },
      boxShadow: {
        glow: '0 30px 60px rgba(32, 42, 72, 0.22)'
      }
    }
  },
  plugins: []
}
