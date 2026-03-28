import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth':    'http://localhost:8000',
      '/stt':     'http://localhost:8000',
      '/query':   'http://localhost:8000',
      '/schemes': 'http://localhost:8000',
    }
  }
})