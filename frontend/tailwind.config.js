/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'mes-dark': '#001529',
        'mes-blue': '#1890ff',
      }
    },
  },
  plugins: [],
}
