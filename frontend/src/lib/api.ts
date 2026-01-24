import { env } from '$env/dynamic/public';
import { auth } from './auth';
import { get } from 'svelte/store';

const API_BASE = env.PUBLIC_API_BASE_URL || '/api';

function getHeaders(includeAuth: boolean = true): HeadersInit {
	const headers: HeadersInit = {
		'Content-Type': 'application/json'
	};
	
	if (includeAuth) {
		const authState = get(auth);
		if (authState.credentials) {
			headers['Authorization'] = `Basic ${authState.credentials}`;
		}
	}
	
	return headers;
}

async function handleResponse(response: Response): Promise<Response> {
	if (response.status === 401) {
		// Unauthorized - clear auth state and redirect to login
		auth.logout();
		if (typeof window !== 'undefined') {
			window.location.href = '/login';
		}
		throw new Error('Unauthorized');
	}
	return response;
}

export interface LookupResponse {
	status: 'found' | 'created' | 'not_found';
	product?: Product;
}

export interface Product {
	id: string;
	gtin: string | null;
	name: string;
	brand: string | null;
	image_url: string | null;
	source: string;
}

export interface InventoryItem {
	id: string;
	product_id: string;
	location: string;
	quantity: number;
	unit: string;
	notes: string | null;
}

export interface InventoryItemCreate {
	product_id: string;
	location: string;
	quantity: number;
	unit?: string;
	notes?: string;
}

export interface ProductCreate {
	gtin?: string;
	name: string;
	brand?: string;
	image_url?: string;
	source?: string;
}

export const api = {
	async checkAuth(): Promise<{ authenticated: boolean; username: string }> {
		const response = await fetch(`${API_BASE}/auth/check`, {
			headers: getHeaders()
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Auth check failed');
		return response.json();
	},

	async lookupBarcode(code: string): Promise<LookupResponse> {
		const response = await fetch(`${API_BASE}/lookup`, {
			method: 'POST',
			headers: getHeaders(),
			body: JSON.stringify({ code })
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Lookup failed');
		return response.json();
	},

	async getProduct(id: string): Promise<Product> {
		const response = await fetch(`${API_BASE}/products/${id}`, {
			headers: getHeaders()
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to fetch product');
		return response.json();
	},

	async listProducts(query?: string): Promise<Product[]> {
		const queryParams = query ? `?query=${encodeURIComponent(query)}` : '';
		const response = await fetch(`${API_BASE}/products${queryParams}`, {
			headers: getHeaders()
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to fetch products');
		return response.json();
	},

	async createProduct(product: ProductCreate): Promise<Product> {
		const response = await fetch(`${API_BASE}/products`, {
			method: 'POST',
			headers: getHeaders(),
			body: JSON.stringify(product)
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to create product');
		return response.json();
	},

	async createInventoryItem(item: InventoryItemCreate): Promise<InventoryItem> {
		const response = await fetch(`${API_BASE}/inventory`, {
			method: 'POST',
			headers: getHeaders(),
			body: JSON.stringify(item)
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to create inventory item');
		return response.json();
	},

	async listInventory(location?: string): Promise<InventoryItem[]> {
		const queryParams = location ? `?location=${encodeURIComponent(location)}` : '';
		const response = await fetch(`${API_BASE}/inventory${queryParams}`, {
			headers: getHeaders()
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to fetch inventory');
		return response.json();
	},

	async adjustInventory(itemId: string, delta: number): Promise<InventoryItem | { status: string; id: string }> {
		const response = await fetch(`${API_BASE}/inventory/${itemId}/adjust`, {
			method: 'POST',
			headers: getHeaders(),
			body: JSON.stringify({ delta, reason: 'adjust' })
		});
		await handleResponse(response);
		if (!response.ok) throw new Error('Failed to adjust inventory');
		return response.json();
	}
};
