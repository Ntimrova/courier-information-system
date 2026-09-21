import { fileURLToPath, URL } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      // У Docker події файлової системи не долітають до контейнера,
      // тому вмикаємо періодичне опитування.
      usePolling: true,
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // Бібліотеки (переважно MUI) зібрані в один vendor-файл. Для внутрішньої
    // системи це нормально: він завантажується один раз і далі береться з кешу.
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        // Розділяємо бандл: бібліотеки змінюються рідко, тож браузер
        // кешує їх між релізами, а не качає все заново.
        manualChunks(id: string) {
          if (id.includes('node_modules')) return 'vendor';
          return undefined;
        },
      },
    },
  },
});
