import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#071013",
        graphite: "#101820",
        glass: "rgba(255,255,255,0.08)",
        cyan: "#67e8f9",
        mint: "#5eead4",
        amber: "#f6c177",
        rose: "#fda4af"
      },
      boxShadow: {
        glow: "0 24px 80px rgba(103,232,249,0.18)",
        panel: "0 18px 60px rgba(0,0,0,0.32)"
      },
      backgroundImage: {
        "mesh": "linear-gradient(135deg, #071013 0%, #101820 44%, #17211f 100%), linear-gradient(90deg, rgba(103,232,249,0.08), rgba(246,193,119,0.08))"
      }
    }
  },
  plugins: []
};

export default config;
