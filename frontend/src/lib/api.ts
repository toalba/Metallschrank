import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_API_BASE_URL || '/api';

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
	async lookupBarcode(code: string): Promise<LookupResponse> {
		const response = await fetch(`${API_BASE}/lookup`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ code })
		});
		if (!response.ok) throw new Error('Lookup failed');
		return response.json();
	},

	async getProduct(id: string): Promise<Product> {
		const response = await fetch(`${API_BASE}/products/${id}`);
		if (!response.ok) throw new Error('Failed to fetch product');
		return response.json();
	},

	async listProducts(query?: string): Promise<Product[]> {
		const queryParams = query ? `?query=${encodeURIComponent(query)}` : '';
		const response = await fetch(`${API_BASE}/products${queryParams}`);
		if (!response.ok) throw new Error('Failed to fetch products');
		return response.json();
	},

	async createProduct(product: ProductCreate): Promise<Product> {
		const response = await fetch(`${API_BASE}/products`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(product)
		});
		if (!response.ok) throw new Error('Failed to create product');
		return response.json();
	},

	async createInventoryItem(item: InventoryItemCreate): Promise<InventoryItem> {
		const response = await fetch(`${API_BASE}/inventory`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(item)
		});
		if (!response.ok) throw new Error('Failed to create inventory item');
		return response.json();
	},

	async listInventory(location?: string): Promise<InventoryItem[]> {
		const queryParams = location ? `?location=${encodeURIComponent(location)}` : '';
		const response = await fetch(`${API_BASE}/inventory${queryParams}`);
		if (!response.ok) throw new Error('Failed to fetch inventory');
		return response.json();
	},

	async adjustInventory(itemId: string, delta: number): Promise<InventoryItem | { status: string; id: string }> {
		const response = await fetch(`${API_BASE}/inventory/${itemId}/adjust`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ delta, reason: 'adjust' })
		});
		if (!response.ok) throw new Error('Failed to adjust inventory');
		return response.json();
	}
};
