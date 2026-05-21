/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#6366f1', light: '#818cf8', dark: '#4f46e5' },
        accent: { DEFAULT: '#f43f5e', light: '#fb7185' },
        surface: { DEFAULT: '#ffffff', dark: '#0f172a' }
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
}