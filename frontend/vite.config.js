import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    // 关键：配置本地开发时的反向代理
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // 你的 Python 后端地址
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // 注意：不要加这一行，因为你后端路由本身就带 /api
      }
    }
  }
})