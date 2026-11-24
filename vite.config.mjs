import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  base: './',
  build: {
    assetsInlineLimit: 0,
    rollupOptions: {
      input: {
        h03: fileURLToPath(new URL('./index.html', import.meta.url)),
        coreDemo: fileURLToPath(new URL('./core-demo.html', import.meta.url)),
        daiyuHuaguoshan: fileURLToPath(new URL('./daiyu-huaguoshan.html', import.meta.url)),
      },
    },
  },
});
