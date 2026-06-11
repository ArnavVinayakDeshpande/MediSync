// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      // ── Node.js / Express (appointments, templates) ─────────────────────
      // '/api': {
      //   target: 'http://localhost:3001',
      //   changeOrigin: true,
      // },

      // ── New patient REST API ─────────────────────────────────────────────
      // IMPORTANT: '/patients' must be listed BEFORE '/patient' below.
      // Vite uses prefix matching — without this order, '/patient' would
      // accidentally intercept '/patients/...' calls.
      //
      // Update the target port/host when the backend team provides the URL.
      '/patients': {
        target: 'http://127.0.0.1:8000 ',  // ← update when finalised
        changeOrigin: true,
      },

      '/visits': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})