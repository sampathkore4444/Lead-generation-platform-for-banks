/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0066CC",
          50: "#E6F0FA",
          100: "#CCE0F5",
          200: "#99C1EB",
          300: "#66A2E1",
          400: "#3383D7",
          500: "#0066CC",
          600: "#0052A3",
          700: "#003D7A",
          800: "#002952",
          900: "#001429",
        },
        accent: {
          DEFAULT: "#FFCC00",
          50: "#FFF9E6",
          100: "#FFF3CC",
          200: "#FFE799",
          300: "#FFDB66",
          400: "#FFCF33",
          500: "#FFCC00",
          600: "#CCA300",
          700: "#997A00",
          800: "#665200",
          900: "#332A00",
        },
        success: "#28A745",
        warning: "#FFC107",
        error: "#DC3545",
        info: "#17A2B8",
      },
      fontFamily: {
        sans: ["Noto Sans Lao", "Noto Sans", "system-ui", "sans-serif"],
      },
      maxWidth: {
        form: "480px",
      },
      boxShadow: {
        card: "0 2px 8px rgba(0, 0, 0, 0.08)",
        "card-hover": "0 4px 12px rgba(0, 0, 0, 0.12)",
      },
    },
  },
  plugins: [],
};
