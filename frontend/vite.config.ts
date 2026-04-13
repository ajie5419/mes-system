import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          'echarts': ['echarts'],
          'vue-vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    }
  },
  server: {
    port: 8899,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true
      }
    }
  }
})
