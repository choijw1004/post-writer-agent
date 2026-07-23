import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // /api 를 FastAPI 로 넘긴다. 개발 중에도 같은 오리진이 되므로
    // CORS 도, EventSource 의 크로스 오리진 제약도 신경 쓸 일이 없다.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
