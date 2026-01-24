import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		host: '0.0.0.0',
		strictPort: true,
		proxy: {
			// Proxy API requests to backend in development
			'/api': {
				target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	preview: {
		port: 5173,
		host: '0.0.0.0',
		strictPort: true
	}
});
