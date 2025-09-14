import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/cam-fov-calc/',
  server: {
    open: '/cam-fov-calc/'
  },
  plugins: [react()],
})
