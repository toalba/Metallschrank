<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import type { InventoryItem, Product } from '$lib/api';

	type InventoryItemWithProduct = InventoryItem & {
		product?: Product;
	};

	let items: InventoryItemWithProduct[] = [];
	let isLoading = false;
	let error: string | null = null;
	let searchLocation = '';
	let adjustingItems = new Set<string>();

	onMount(() => {
		loadInventory();
	});

	async function loadInventory(location?: string) {
		isLoading = true;
		error = null;

		try {
			const inventoryItems = await api.listInventory(location);
			// Fetch product details for each item
			items = await Promise.all(
				inventoryItems.map(async (item): Promise<InventoryItemWithProduct> => {
					try {
						const product = await api.getProduct(item.product_id);
						return { ...item, product };
					} catch {
						// If product fetch fails, return item without product
						return item;
					}
				})
			);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Fehler beim Laden des Inventars';
		} finally {
			isLoading = false;
		}
	}

	async function handleSearch() {
		const location = searchLocation.trim() || undefined;
		await loadInventory(location);
	}

	function clearSearch() {
		searchLocation = '';
		loadInventory();
	}

	async function adjustQuantity(itemId: string, delta: number) {
		adjustingItems.add(itemId);
		adjustingItems = adjustingItems; // Trigger reactivity

		try {
			const result = await api.adjustInventory(itemId, delta);
			
			// If item was deleted (quantity reached 0), remove from list
			if (result && 'status' in result && result.status === 'deleted') {
				items = items.filter((item) => item.id !== itemId);
			} else {
				// Otherwise update the item in the list, preserving the product data
				items = items.map((item) => {
					if (item.id === itemId) {
						// Merge the updated item with the existing product data
						return { ...result, product: item.product };
					}
					return item;
				});
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Fehler beim Anpassen der Menge';
			// Reload to ensure consistency
			setTimeout(() => loadInventory(searchLocation.trim() || undefined), 1000);
		} finally {
			adjustingItems.delete(itemId);
			adjustingItems = adjustingItems;
		}
	}

	function getLocationParts(location: string): string[] {
		return location.split('/').map((part) => part.trim());
	}
</script>

<svelte:head>
	<title>Inventar - Metallschrank</title>
</svelte:head>

<div class="inventory-page">
	<div class="header">
		<h1>Inventar</h1>
		<a href="/scan" class="btn-primary">+ Artikel hinzufügen</a>
	</div>

	<div class="search-section">
		<form on:submit|preventDefault={handleSearch} class="search-form">
			<div class="search-input-group">
				<input
					type="text"
					bind:value={searchLocation}
					placeholder="Nach Standort filtern..."
					disabled={isLoading}
				/>
				<button type="submit" class="btn-search" disabled={isLoading}>Suchen</button>
				{#if searchLocation}
					<button type="button" class="btn-clear" on:click={clearSearch} disabled={isLoading}>
						✕
					</button>
				{/if}
			</div>
		</form>
	</div>

	{#if error}
		<div class="error-message">
			<p>{error}</p>
			<button type="button" class="btn-retry" on:click={() => loadInventory()}>Erneut versuchen</button>
		</div>
	{/if}

	{#if isLoading}
		<div class="loading">
			<p>Lade Inventar...</p>
		</div>
	{:else if items.length === 0}
		<div class="empty-state">
			{#if searchLocation}
				<p>Keine Artikel gefunden für Standort "{searchLocation}"</p>
				<button type="button" class="btn-secondary" on:click={clearSearch}>Filter entfernen</button>
			{:else}
				<p>Keine Artikel im Inventar</p>
				<a href="/scan" class="btn-primary">Ersten Artikel hinzufügen</a>
			{/if}
		</div>
	{:else}
		<div class="inventory-list">
			<div class="list-header">
				<span class="count">{items.length} Artikel{items.length !== 1 ? '' : ''}</span>
			</div>

			{#each items as item (item.id)}
				<div class="inventory-item">
					{#if item.product?.image_url}
						<div class="item-image">
							<img src={item.product.image_url} alt={item.product.name} />
						</div>
					{/if}

					<div class="item-info">
						<h3 class="item-name">
							{#if item.product}
								{item.product.name}
							{:else}
								Produkt ID: {item.product_id}
							{/if}
						</h3>
						{#if item.product?.brand}
							<p class="brand">{item.product.brand}</p>
						{/if}
						<div class="location">
							{#each getLocationParts(item.location) as part, i}
								{#if i > 0}
									<span class="separator">→</span>
								{/if}
								<span class="location-part">{part}</span>
							{/each}
						</div>
						{#if item.notes}
							<p class="notes">{item.notes}</p>
						{/if}
					</div>

					<div class="item-controls">
						<div class="quantity-info">
							<span class="quantity">{item.quantity}</span>
							<span class="unit">{item.unit}</span>
						</div>

						<div class="adjust-buttons">
							<button
								type="button"
								class="btn-adjust btn-minus"
								on:click={() => adjustQuantity(item.id, -1)}
								disabled={adjustingItems.has(item.id)}
								title="Menge um 1 verringern"
							>
								−1
							</button>
							<button
								type="button"
								class="btn-adjust btn-plus"
								on:click={() => adjustQuantity(item.id, 1)}
								disabled={adjustingItems.has(item.id)}
								title="Menge um 1 erhöhen"
							>
								+1
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.inventory-page {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem 1rem;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		flex-wrap: wrap;
		gap: 1rem;
	}

	h1 {
		margin: 0;
		color: #333;
	}

	.btn-primary {
		padding: 0.75rem 1.5rem;
		background: #007bff;
		color: white;
		text-decoration: none;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
		display: inline-block;
	}

	.btn-primary:hover {
		background: #0056b3;
	}

	.search-section {
		margin-bottom: 2rem;
	}

	.search-form {
		width: 100%;
	}

	.search-input-group {
		display: flex;
		gap: 0.5rem;
		max-width: 600px;
	}

	.search-input-group input {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.search-input-group input:focus {
		outline: none;
		border-color: #007bff;
	}

	.btn-search,
	.btn-clear {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
	}

	.btn-search {
		background: #007bff;
		color: white;
	}

	.btn-search:hover:not(:disabled) {
		background: #0056b3;
	}

	.btn-clear {
		background: #6c757d;
		color: white;
		padding: 0.75rem 1rem;
	}

	.btn-clear:hover:not(:disabled) {
		background: #5a6268;
	}

	.btn-search:disabled,
	.btn-clear:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-secondary {
		padding: 0.75rem 1.5rem;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
	}

	.btn-secondary:hover {
		background: #5a6268;
	}

	.loading,
	.empty-state {
		text-align: center;
		padding: 3rem 1rem;
		color: #666;
	}

	.empty-state {
		background: #f8f9fa;
		border-radius: 8px;
	}

	.empty-state p {
		margin-bottom: 1rem;
		font-size: 1.1rem;
	}

	.error-message {
		margin-bottom: 2rem;
		padding: 1rem;
		background: #f8d7da;
		color: #721c24;
		border-radius: 4px;
		border: 1px solid #f5c6cb;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.error-message p {
		margin: 0;
		flex: 1;
	}

	.btn-retry {
		padding: 0.5rem 1rem;
		background: #721c24;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		white-space: nowrap;
	}

	.btn-retry:hover {
		background: #5a161a;
	}

	.inventory-list {
		background: white;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.list-header {
		padding: 1rem 1.5rem;
		background: #f8f9fa;
		border-bottom: 1px solid #dee2e6;
	}

	.count {
		font-weight: 500;
		color: #666;
	}

	.inventory-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e9ecef;
		gap: 1.5rem;
	}

	.inventory-item:last-child {
		border-bottom: none;
	}

	.item-image {
		flex-shrink: 0;
	}

	.item-image img {
		width: 80px;
		height: 80px;
		object-fit: contain;
		border-radius: 4px;
		background: #f8f9fa;
		padding: 0.25rem;
	}

	.item-info {
		flex: 1;
		min-width: 0;
	}

	.item-name {
		margin: 0 0 0.5rem 0;
		font-size: 1.1rem;
		color: #333;
	}

	.brand {
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
		font-weight: 500;
		color: #555;
	}

	.location {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
	}

	.location-part {
		padding: 0.25rem 0.5rem;
		background: #e9ecef;
		border-radius: 4px;
		color: #495057;
	}

	.separator {
		color: #adb5bd;
	}

	.notes {
		margin: 0.5rem 0 0 0;
		font-size: 0.9rem;
		color: #666;
		font-style: italic;
	}

	.item-controls {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-shrink: 0;
	}

	.quantity-info {
		text-align: center;
		min-width: 80px;
	}

	.quantity {
		display: block;
		font-size: 1.5rem;
		font-weight: bold;
		color: #333;
	}

	.unit {
		display: block;
		font-size: 0.875rem;
		color: #666;
	}

	.adjust-buttons {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.btn-adjust {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		font-size: 0.9rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.2s;
		min-width: 50px;
	}

	.btn-plus {
		background: #28a745;
		color: white;
	}

	.btn-plus:hover:not(:disabled) {
		background: #218838;
	}

	.btn-minus {
		background: #dc3545;
		color: white;
	}

	.btn-minus:hover:not(:disabled) {
		background: #c82333;
	}

	.btn-adjust:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	@media (max-width: 768px) {
		.inventory-page {
			padding: 0.75rem;
		}

		.header {
			flex-direction: column;
			align-items: stretch;
			margin-bottom: 1.5rem;
		}

		.header h1 {
			text-align: center;
			font-size: 1.5rem;
			margin-bottom: 0.75rem;
		}

		.btn-primary {
			width: 100%;
			padding: 1rem 1.5rem;
			min-height: 48px;
			font-size: 1.05rem;
		}

		.search-input-group {
			max-width: none;
		}

		.search-input-group input {
			font-size: 16px; /* Prevents iOS zoom */
			padding: 0.875rem;
		}

		.btn-search,
		.btn-clear {
			padding: 0.875rem 1.25rem;
			min-height: 48px;
		}

		.inventory-item {
			flex-direction: column;
			align-items: stretch;
			padding: 1rem;
		}

		.item-image img {
			width: 80px;
			height: 80px;
		}

		.item-controls {
			flex-direction: row;
			justify-content: space-between;
			margin-top: 1rem;
			gap: 0.75rem;
		}

		.adjust-buttons {
			flex-direction: row;
			gap: 0.5rem;
		}

		.adjust-buttons button {
			flex: 1;
			padding: 0.75rem 1rem;
			min-height: 48px;
			font-size: 1.1rem;
			min-width: 0;
		}

		.product-name {
			font-size: 1rem;
		}

		.quantity {
			font-size: 1.1rem;
		}

		.list-header {
			padding: 0.875rem 1rem;
		}
	}

	@media (max-width: 390px) {
		.inventory-page {
			padding: 0.5rem;
		}

		.header {
			margin-bottom: 1rem;
		}

		.header h1 {
			font-size: 1.25rem;
			margin-bottom: 0.5rem;
		}

		.btn-primary {
			padding: 0.875rem 1rem;
			font-size: 1rem;
		}

		.search-input-group input {
			padding: 0.75rem;
		}

		.btn-search,
		.btn-clear {
			padding: 0.75rem 1rem;
		}

		.inventory-item {
			padding: 0.75rem;
		}

		.item-image img {
			width: 70px;
			height: 70px;
		}

		.product-name {
			font-size: 0.95rem;
		}

		.brand,
		.location-text {
			font-size: 0.85rem;
		}

		.quantity {
			font-size: 1rem;
		}

		.adjust-buttons button {
			padding: 0.65rem 0.75rem;
			font-size: 1rem;
		}

		.list-header {
			padding: 0.75rem;
		}

		.count {
			font-size: 0.9rem;
		}
	}
</style>
