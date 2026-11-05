import { defineConfig } from 'vite';
export default defineConfig({esbuild: {jsx: 'automatic', jsxImportSource: 'preact'}, server: {port: 5173, strictPort: true, proxy: {'/api': 'http://127.0.0.1:8000', '/admin': 'http://127.0.0.1:8000', '/static': 'http://127.0.0.1:8000'}}, build: {outDir: 'dist'}});
