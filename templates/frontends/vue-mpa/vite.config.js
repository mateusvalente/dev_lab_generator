import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      input: {
        categories: resolve(__dirname, 'categories.html'),
        products: resolve(__dirname, 'products.html')
      }
    }
  },
  server: { host: '0.0.0.0', port: Number(process.env.PORT || 3000) }
})
