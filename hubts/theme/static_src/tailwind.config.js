module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#FFEB99',
          DEFAULT: '#FFD700',
          dark: '#DAA520',
        },
        secondary: {
          DEFAULT: '#4B0082',
        },
        accent: {
          DEFAULT: '#FF8C00',
        },
      },
    },
  },
  plugins: [],
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  darkMode: 'class',
}
