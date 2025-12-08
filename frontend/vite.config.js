import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      // 1. 读取并设置前端端口
      // 如果 .env 里没配，就默认回退到 5173
      port: parseInt(env.VITE_PORT) || 5173,
      
      // 2. 监听所有网络接口（服务器部署必需）
      host: env.VITE_HOST || '0.0.0.0',
      
      // 3. 允许的主机名（解决 Vite 的 Host header 检查）
      allowedHosts: env.VITE_ALLOWED_HOSTS 
        ? env.VITE_ALLOWED_HOSTS.split(',').map(h => h.trim())
        : ['localhost', '127.0.0.1'],
      
      // 4. 代理配置
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET || 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})