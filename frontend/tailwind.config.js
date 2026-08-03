/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: '#0a0a1a',
        navy: '#0f0f2e',
        indigo: '#6366f1',
        violet: '#8b5cf6',
        cyan: '#06b6d4',
        glass: 'rgba(255,255,255,0.05)',
      },
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      animation: {
        'glow-pulse': 'glow-pulse 3s infinite alternate',
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
        'counter': 'counter 2s ease-out forwards',
        'shimmer': 'shimmer 2s linear infinite',
      },
      boxShadow: {
        'glow-indigo': '0 0 20px rgba(99, 102, 241, 0.4)',
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.4)',
        'glow-violet': '0 0 20px rgba(139, 92, 246, 0.4)',
      },
      keyframes: {
        'glow-pulse': {
          '0%': { opacity: '0.5' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        counter: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
