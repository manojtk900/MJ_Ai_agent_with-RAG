/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jarvis: {
          bg: "#020613",
          card: "rgba(5, 15, 35, 0.75)",
          elevated: "rgba(10, 25, 55, 0.85)",
          border: "rgba(0, 240, 255, 0.25)",
          borderGlow: "rgba(0, 240, 255, 0.6)",
          cyan: "#00f0ff",
          blue: "#0072ff",
          purple: "#7000ff",
          green: "#00ff9d",
          red: "#ff0055",
          amber: "#ffb700",
          text: "#e0f7fc",
          muted: "#5a7b9c",
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        hud: ['"Orbitron"', 'sans-serif'],
      },
      boxShadow: {
        neonCyan: '0 0 20px rgba(0, 240, 255, 0.35), 0 0 40px rgba(0, 240, 255, 0.15)',
        neonBlue: '0 0 20px rgba(0, 114, 255, 0.35), 0 0 40px rgba(0, 114, 255, 0.15)',
        neonGreen: '0 0 20px rgba(0, 255, 157, 0.35)',
        neonRed: '0 0 20px rgba(255, 0, 85, 0.35)',
        orbInner: 'inset 0 0 30px #00f0ff, 0 0 50px #00f0ff',
      },
      animation: {
        'spin-slow': 'spin 12s linear infinite',
        'spin-reverse-slow': 'spin-reverse 16s linear infinite',
        'pulse-glow': 'pulseGlow 2.5s ease-in-out infinite',
        'scanline': 'scanline 8s linear infinite',
        'hud-pulse': 'hudPulse 2s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
      },
      keyframes: {
        'spin-reverse': {
          '0%': { transform: 'rotate(360deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: 0.8, filter: 'drop-shadow(0 0 15px #00f0ff)' },
          '50%': { opacity: 1, filter: 'drop-shadow(0 0 35px #00f0ff)' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        },
        hudPulse: {
          '0%, 100%': { borderColor: 'rgba(0, 240, 255, 0.3)' },
          '50%': { borderColor: 'rgba(0, 240, 255, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
}
