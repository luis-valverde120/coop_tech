/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        coopverde: '#008A4B',
        coopverdeclaro: '#E6F3ED',
        cooprojoclaro: '#FDECEF',
        cooprojo: '#E53E3E',
        coopnaranja: '#ED8936',
        coopamarillo: '#ECC94B',
        coopgris: '#F8F9FA'
      }
    },
  },
  plugins: [],
}
