import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface AuthState {
	isAuthenticated: boolean;
	username: string | null;
	credentials: string | null; // Base64 encoded username:password
}

const STORAGE_KEY = 'metallschrank_auth';

function createAuthStore() {
	// Load initial state from localStorage
	const initial: AuthState = {
		isAuthenticated: false,
		username: null,
		credentials: null
	};

	if (browser) {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			try {
				const parsed = JSON.parse(stored);
				initial.isAuthenticated = parsed.isAuthenticated || false;
				initial.username = parsed.username || null;
				initial.credentials = parsed.credentials || null;
			} catch {
				// Invalid stored data, use defaults
			}
		}
	}

	const { subscribe, set, update } = writable<AuthState>(initial);

	return {
		subscribe,
		
		login(username: string, password: string) {
			const credentials = btoa(`${username}:${password}`);
			const state: AuthState = {
				isAuthenticated: true,
				username,
				credentials
			};
			
			if (browser) {
				localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
			}
			
			set(state);
		},
		
		logout() {
			const state: AuthState = {
				isAuthenticated: false,
				username: null,
				credentials: null
			};
			
			if (browser) {
				localStorage.removeItem(STORAGE_KEY);
			}
			
			set(state);
		},
		
		getAuthHeader(): string | null {
			let credentials: string | null = null;
			subscribe(state => {
				credentials = state.credentials;
			})();
			return credentials ? `Basic ${credentials}` : null;
		}
	};
}

export const auth = createAuthStore();
