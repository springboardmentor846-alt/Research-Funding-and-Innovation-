/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  safelist: [
    "text-primary-600", "text-purple-600", "text-green-600", "text-amber-600", "text-red-600", "text-blue-600",
    "bg-primary-50", "bg-purple-50", "bg-green-50", "bg-amber-50", "bg-red-50", "bg-blue-50",
    "border-primary-500", "border-primary-300", "border-primary-200",
    "bg-primary-100", "bg-purple-100", "bg-green-100", "bg-amber-100", "bg-red-100", "bg-blue-100", "bg-slate-100",
    "text-primary-800", "text-purple-800", "text-green-800", "text-amber-800", "text-red-800", "text-blue-800", "text-slate-800", "text-slate-700",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
        },
        accent: {
          500: "#8b5cf6",
          600: "#7c3aed",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.4s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: 0 },
          "100%": { transform: "translateY(0)", opacity: 1 },
        },
      },
    },
  },
  plugins: [],
};
