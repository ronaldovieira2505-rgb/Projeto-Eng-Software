/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        mack: {
          bg:       "#0f1117",
          surface:  "#13151d",
          border:   "#1f2235",
          hover:    "#161824",
          "nav-active": "#1a2640",
        },
      },
    },
  },
  plugins: [],
};
