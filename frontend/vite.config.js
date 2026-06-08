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
      // Node.js / Express — appointments, old excel stuff
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      // Python / FastAPI — patients and message templates
      '/patient': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/templates': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})