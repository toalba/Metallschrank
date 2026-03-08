<script lang="ts">
	import { api } from '$lib/api';
	import type { LookupResponse, InventoryItemCreate, InventoryItem, Product, ProductCreate } from '$lib/api';
	import BarcodeScanner from '$lib/components/BarcodeScanner.svelte';

	type InventoryItemWithProduct = InventoryItem & {
		product?: Product;
	};

	let scanner: BarcodeScanner;
	let barcodeInput = '';
	let lookupResult: LookupResponse | null = null;
	let isLookingUp = false;
	let lookupError: string | null = null;

	// Existing inventory items for this product
	let existingItems: InventoryItemWithProduct[] = [];
	let isLoadingExisting = false;
	let adjustingItems = new Set<string>();

	// Inventory form state
	let location = '';
	let quantity = 1;
	let unit = 'Stück';
	let notes = '';
	let isCreatingInventory = false;
	let inventoryError: string | null = null;
	let inventorySuccess = false;

	// Manual product creation state
	let showManualForm = false;
	let manualProduct = {
		name: '',
		brand: '',
		image_url: '',
		gtin: ''
	};
	let isCreatingProduct = false;
	let productError: string | null = null;

	function isValidBarcode(code: string): boolean {
		// GTIN-8, GTIN-12 (UPC), GTIN-13 (EAN), GTIN-14
		return /^\d{8,14}$/.test(code);
	}

	async function handleLookup() {
		if (!barcodeInput.trim()) return;

		if (!isValidBarcode(barcodeInput.trim())) {
			lookupError = 'Ungültiger Barcode. Bitte eine 8-14 stellige Nummer eingeben.';
			return;
		}

		isLookingUp = true;
		lookupError = null;
		lookupResult = null;
		inventorySuccess = false;
		existingItems = [];

		try {
			lookupResult = await api.lookupBarcode(barcodeInput.trim());
			
			// If product found, load inventory
			if (lookupResult?.product) {
				await loadExistingInventory(lookupResult.product.id);
			}
		} catch (err) {
			lookupError = err instanceof Error ? err.message : 'Fehler beim Nachschlagen';
		} finally {
			isLookingUp = false;
		}
	}

	async function loadExistingInventory(productId: string) {
		isLoadingExisting = true;
		try {
			const allItems = await api.listInventory();
			// Filter items for this specific product
			existingItems = allItems.filter(item => item.product_id === productId)
				.map(item => ({ ...item, product: lookupResult?.product }));
		} catch (err) {
			console.error('Failed to load existing inventory:', err);
		} finally {
			isLoadingExisting = false;
		}
	}

	async function adjustQuantity(itemId: string, delta: number) {
		adjustingItems.add(itemId);
		adjustingItems = adjustingItems;

		try {
			const result = await api.adjustInventory(itemId, delta);
			
			// If item was deleted, remove from list
			if (result && 'status' in result && result.status === 'deleted') {
				existingItems = existingItems.filter((item) => item.id !== itemId);
			} else {
				// Otherwise update the item
				existingItems = existingItems.map((item) => {
					if (item.id === itemId) {
						return { ...result, product: item.product };
					}
					return item;
				});
			}
		} catch (err) {
			inventoryError = err instanceof Error ? err.message : 'Fehler beim Anpassen der Menge';
		} finally {
			adjustingItems.delete(itemId);
			adjustingItems = adjustingItems;
		}
	}

	function handleScan(event: CustomEvent<string>) {
		barcodeInput = event.detail;
		scanner?.stop();
		handleLookup();
	}

	function showManualProductForm() {
		showManualForm = true;
		productError = null;
		// Pre-fill with barcode if available
		manualProduct.gtin = barcodeInput.trim();
	}

	function cancelManualForm() {
		showManualForm = false;
		manualProduct = { name: '', brand: '', image_url: '', gtin: '' };
		productError = null;
	}

	async function handleCreateManualProduct(event: Event) {
		event.preventDefault();
		
		if (!manualProduct.name.trim()) {
			productError = 'Produktname ist erforderlich';
			return;
		}

		isCreatingProduct = true;
		productError = null;

		try {
			const newProduct = await api.createProduct({
				gtin: manualProduct.gtin.trim() || undefined,
				name: manualProduct.name.trim(),
				brand: manualProduct.brand.trim() || undefined,
				image_url: manualProduct.image_url.trim() || undefined,
				source: 'manual'
			});

			// Set as lookup result so user can add to inventory
			lookupResult = {
				status: 'created',
				product: newProduct
			};

			// Load existing inventory for this product
			await loadExistingInventory(newProduct.id);

			// Reset manual form
			showManualForm = false;
			manualProduct = { name: '', brand: '', image_url: '', gtin: '' };
		} catch (err) {
			productError = err instanceof Error ? err.message : 'Fehler beim Erstellen des Produkts';
		} finally {
			isCreatingProduct = false;
		}
	}

	async function handleSubmitInventory(event: Event) {
		event.preventDefault();
		if (!lookupResult?.product) return;

		isCreatingInventory = true;
		inventoryError = null;
		inventorySuccess = false;

		try {
			const item: InventoryItemCreate = {
				product_id: lookupResult.product.id,
				location: location.trim(),
				quantity,
				unit,
				notes: notes.trim() || undefined
			};

			await api.createInventoryItem(item);
			inventorySuccess = true;

			// Reset form
			location = '';
			quantity = 1;
			unit = 'Stück';
			notes = '';

			// Reload existing inventory
			await loadExistingInventory(lookupResult.product.id);

			// Clear success message after delay
			setTimeout(() => {
				inventorySuccess = false;
			}, 2000);
		} catch (err) {
			inventoryError = err instanceof Error ? err.message : 'Fehler beim Erstellen';
		} finally {
			isCreatingInventory = false;
		}
	}

	function getStatusClass(status: string): string {
		switch (status) {
			case 'found':
				return 'status-found';
			case 'created':
				return 'status-created';
			case 'not_found':
				return 'status-not-found';
			default:
				return '';
		}
	}

	function getStatusText(status: string): string {
		switch (status) {
			case 'found':
				return 'Gefunden in Datenbank';
			case 'created':
				return 'Neu erstellt';
			case 'not_found':
				return 'Nicht gefunden';
			default:
				return status;
		}
	}
</script>

<svelte:head>
	<title>Barcode scannen - Metallschrank</title>
</svelte:head>

<div class="scan-page">
	<h1>Barcode scannen</h1>

	<div class="scanner-section">
		<h2>Kamera-Scanner</h2>
		<BarcodeScanner bind:this={scanner} on:scan={handleScan} />
	</div>

	<div class="divider">
		<span>oder</span>
	</div>

	<div class="manual-section">
		<h2>Manuelle Eingabe</h2>
		<form on:submit|preventDefault={handleLookup} class="lookup-form">
			<div class="form-group">
				<label for="barcode-input">Barcode / EAN / GTIN</label>
				<input
					id="barcode-input"
					type="text"
					bind:value={barcodeInput}
					placeholder="z.B. 4006040038043"
					disabled={isLookingUp}
				/>
			</div>
			<button type="submit" class="btn-primary" disabled={isLookingUp || !barcodeInput.trim()}>
				{isLookingUp ? 'Suche...' : 'Nachschlagen'}
			</button>
		</form>

		{#if lookupError}
			<div class="error-message">
				<p>{lookupError}</p>
			</div>
		{/if}
	</div>

	{#if lookupResult}
		<div class="result-section">
			<div class="status-indicator {getStatusClass(lookupResult.status)}">
				{getStatusText(lookupResult.status)}
			</div>

			{#if lookupResult.product}
				<div class="product-info">
					{#if lookupResult.product.image_url}
						<div class="product-image">
							<img src={lookupResult.product.image_url} alt={lookupResult.product.name} />
						</div>
					{/if}
					<div class="product-details">
						<h3>{lookupResult.product.name}</h3>
						{#if lookupResult.product.brand}
							<p class="brand">{lookupResult.product.brand}</p>
						{/if}
						{#if lookupResult.product.gtin}
							<p class="gtin">GTIN: {lookupResult.product.gtin}</p>
						{/if}
						<p class="source">Quelle: {lookupResult.product.source}</p>
					</div>
				</div>

				{#if existingItems.length > 0}
					<div class="existing-inventory">
						<h3>Im Inventar vorhanden:</h3>
						<div class="inventory-list">
							{#each existingItems as item (item.id)}
								<div class="inventory-item">
									<div class="item-info">
										<div class="location">{item.location}</div>
										<div class="quantity-info">
											{item.quantity} {item.unit}
										</div>
										{#if item.notes}
											<div class="notes">{item.notes}</div>
										{/if}
									</div>
									<div class="item-actions">
										<button
											type="button"
											class="btn-adjust"
											on:click={() => adjustQuantity(item.id, -1)}
											disabled={adjustingItems.has(item.id)}
										>
											-1
										</button>
										<button
											type="button"
											class="btn-adjust"
											on:click={() => adjustQuantity(item.id, 1)}
											disabled={adjustingItems.has(item.id)}
										>
											+1
										</button>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<form on:submit={handleSubmitInventory} class="inventory-form">
					<h3>Zum Inventar hinzufügen</h3>

					<div class="form-group">
						<label for="location">Standort *</label>
						<select
							id="location"
							bind:value={location}
							required
							disabled={isCreatingInventory}
						>
							<option value="">Bitte wählen...</option>
							<option value="Testschrank">Testschrank</option>
							<option value="Metallschrank/Fach1">Metallschrank/Fach1</option>
							<option value="Metallschrank/Fach2">Metallschrank/Fach2</option>
							<option value="Metallschrank/Fach3">Metallschrank/Fach3</option>
							<option value="Metallschrank/Fach4">Metallschrank/Fach4</option>
						</select>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="quantity">Menge *</label>
							<input
								id="quantity"
								type="number"
								bind:value={quantity}
								min="1"
								step="1"
								required
								disabled={isCreatingInventory}
							/>
						</div>

						<div class="form-group">
							<label for="unit">Einheit</label>
							<select id="unit" bind:value={unit} disabled={isCreatingInventory}>
								<option value="Stück">Stück</option>
								<option value="Packung">Packung</option>
								<option value="Dose">Dose</option>
								<option value="Flasche">Flasche</option>
								<option value="kg">kg</option>
								<option value="g">g</option>
								<option value="L">L</option>
								<option value="ml">ml</option>
							</select>
						</div>
					</div>

					<div class="form-group">
						<label for="notes">Notizen</label>
						<textarea
							id="notes"
							bind:value={notes}
							placeholder="Optionale Notizen..."
							rows="3"
							disabled={isCreatingInventory}
						></textarea>
					</div>

					<button type="submit" class="btn-success" disabled={isCreatingInventory}>
						{isCreatingInventory ? 'Wird hinzugefügt...' : 'Zum Inventar hinzufügen'}
					</button>
				</form>

				{#if inventoryError}
					<div class="error-message">
						<p>{inventoryError}</p>
					</div>
				{/if}

				{#if inventorySuccess}
					<div class="success-message">
						<p>✓ Artikel erfolgreich zum Inventar hinzugefügt!</p>
					</div>
				{/if}
			{:else}
				<div class="not-found-message">
					<p>Kein Produkt für diesen Code gefunden.</p>
					<p class="hint">
						Das Produkt konnte weder in der lokalen Datenbank noch über externe Quellen gefunden
						werden.
					</p>
					<button type="button" class="btn-primary" on:click={showManualProductForm}>
						Produkt manuell hinzufügen
					</button>
				</div>
			{/if}
		</div>
	{/if}

	{#if showManualForm}
		<div class="manual-product-section">
			<h2>Produkt manuell hinzufügen</h2>
			
			<form on:submit={handleCreateManualProduct} class="product-form">
				<div class="form-group">
					<label for="manual-gtin">Barcode / EAN / GTIN (optional)</label>
					<input
						id="manual-gtin"
						type="text"
						bind:value={manualProduct.gtin}
						placeholder="z.B. 4006040038043 (leer lassen falls kein Barcode)"
						disabled={isCreatingProduct}
					/>
					<small class="hint">Leer lassen für Produkte ohne Barcode</small>
				</div>

				<div class="form-group">
					<label for="manual-name">Produktname *</label>
					<input
						id="manual-name"
						type="text"
						bind:value={manualProduct.name}
						placeholder="z.B. Apfelsaft naturtrüb"
						required
						disabled={isCreatingProduct}
					/>
				</div>

				<div class="form-group">
					<label for="manual-brand">Marke (optional)</label>
					<input
						id="manual-brand"
						type="text"
						bind:value={manualProduct.brand}
						placeholder="z.B. Valensina"
						disabled={isCreatingProduct}
					/>
				</div>

				<div class="form-group">
					<label for="manual-image">Bild-URL (optional)</label>
					<input
						id="manual-image"
						type="url"
						bind:value={manualProduct.image_url}
						placeholder="https://..."
						disabled={isCreatingProduct}
					/>
				</div>

				{#if productError}
					<div class="error-message">
						<p>{productError}</p>
					</div>
				{/if}

				<div class="form-actions">
					<button type="submit" class="btn-success" disabled={isCreatingProduct}>
						{isCreatingProduct ? 'Wird erstellt...' : 'Produkt erstellen'}
					</button>
					<button type="button" class="btn-secondary" on:click={cancelManualForm} disabled={isCreatingProduct}>
						Abbrechen
					</button>
				</div>
			</form>
		</div>
	{/if}

	<div class="divider">
		<span>oder</span>
	</div>

	<div class="no-barcode-section">
		<h2>Produkt ohne Barcode hinzufügen</h2>
		<p class="hint">Für handgemachte Produkte, lose Waren oder Artikel ohne Barcode</p>
		<button type="button" class="btn-secondary" on:click={() => { barcodeInput = ''; showManualProductForm(); }}>
			Neues Produkt ohne Barcode anlegen
		</button>
	</div>
</div>

<style>
	.scan-page {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem 1rem;
	}

	h1 {
		text-align: center;
		margin-bottom: 2rem;
		color: #333;
	}

	h2 {
		font-size: 1.25rem;
		margin-bottom: 1rem;
		color: #555;
	}

	h3 {
		font-size: 1.1rem;
		margin-bottom: 1rem;
		color: #333;
	}

	.scanner-section,
	.manual-section,
	.result-section {
		margin-bottom: 2rem;
	}

	.divider {
		text-align: center;
		margin: 2rem 0;
		position: relative;
	}

	.divider::before,
	.divider::after {
		content: '';
		position: absolute;
		top: 50%;
		width: 40%;
		height: 1px;
		background: #ddd;
	}

	.divider::before {
		left: 0;
	}

	.divider::after {
		right: 0;
	}

	.divider span {
		background: white;
		padding: 0 1rem;
		color: #999;
	}

	.lookup-form {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.lookup-form .form-group {
		flex: 1;
		min-width: 200px;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #555;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
		font-family: inherit;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #007bff;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	@media (max-width: 640px) {
		.form-row {
			grid-template-columns: 1fr;
			gap: 0;
		}
	}

	.btn-primary,
	.btn-success {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
		min-height: 44px;
	}

	@media (max-width: 768px) {
		.btn-primary,
		.btn-success {
			padding: 1rem 1.5rem;
			font-size: 1.05rem;
			min-height: 48px;
		}
	}

	.btn-primary {
		background: #007bff;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: #0056b3;
	}

	.btn-success {
		background: #28a745;
		color: white;
		width: 100%;
	}

	.btn-success:hover:not(:disabled) {
		background: #218838;
	}

	.btn-primary:disabled,
	.btn-success:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.status-indicator {
		padding: 0.75rem 1rem;
		border-radius: 4px;
		font-weight: 500;
		text-align: center;
		margin-bottom: 1rem;
	}

	.status-found {
		background: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.status-created {
		background: #d1ecf1;
		color: #0c5460;
		border: 1px solid #bee5eb;
	}

	.status-not-found {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.product-info {
		display: flex;
		gap: 1.5rem;
		padding: 1.5rem;
		background: #f8f9fa;
		border-radius: 8px;
		margin-bottom: 2rem;
	}

	@media (max-width: 768px) {
		.product-info {
			flex-direction: column;
			padding: 1rem;
			gap: 1rem;
		}
	}

	.product-image {
		flex-shrink: 0;
	}

	.product-image img {
		width: 150px;
		height: 150px;
		object-fit: contain;
		border-radius: 4px;
		background: white;
		padding: 0.5rem;
	}

	.product-details {
		flex: 1;
	}

	.product-details h3 {
		margin: 0 0 0.5rem 0;
	}

	.product-details p {
		margin: 0.25rem 0;
		color: #666;
	}

	.brand {
		font-weight: 500;
		color: #555 !important;
	}

	.gtin,
	.source {
		font-size: 0.875rem;
	}

	.inventory-form {
		padding: 1.5rem;
		background: #fff;
		border: 2px solid #e9ecef;
		border-radius: 8px;
	}

	.error-message,
	.success-message,
	.not-found-message {
		margin-top: 1rem;
		padding: 1rem;
		border-radius: 4px;
	}

	.error-message {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.success-message {
		background: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.not-found-message {
		background: #fff3cd;
		color: #856404;
		border: 1px solid #ffeaa7;
	}

	.not-found-message button {
		margin-top: 1rem;
	}

	.manual-product-section,
	.no-barcode-section {
		margin: 2rem 0;
		padding: 1.5rem;
		background: #f8f9fa;
		border-radius: 8px;
		border: 2px dashed #dee2e6;
	}

	.manual-product-section h2,
	.no-barcode-section h2 {
		margin-top: 0;
		color: #333;
	}

	.product-form {
		margin-top: 1.5rem;
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		margin-top: 1.5rem;
	}

	.form-actions button {
		flex: 1;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
		transition: background 0.2s;
		min-height: 44px;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #5a6268;
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.no-barcode-section .hint {
		margin: 0.5rem 0 1rem 0;
		color: #666;
		font-size: 0.95rem;
	}

	.existing-inventory {
		margin: 2rem 0;
		padding: 1.5rem;
		background: #f8f9fa;
		border-radius: 8px;
	}

	.existing-inventory h3 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.inventory-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.inventory-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		background: white;
		border-radius: 6px;
		border: 1px solid #dee2e6;
	}

	.item-info {
		flex: 1;
	}

	.item-info .location {
		font-weight: 600;
		color: #333;
		margin-bottom: 0.25rem;
	}

	.item-info .quantity-info {
		color: #666;
		font-size: 0.95rem;
	}

	.item-info .notes {
		margin-top: 0.25rem;
		font-size: 0.875rem;
		color: #999;
		font-style: italic;
	}

	.item-actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn-adjust {
		padding: 0.5rem 1rem;
		border: 1px solid #dee2e6;
		background: white;
		border-radius: 4px;
		cursor: pointer;
		font-weight: 600;
		transition: all 0.2s;
		min-width: 50px;
		min-height: 44px;
	}

	@media (max-width: 768px) {
		.btn-adjust {
			padding: 0.75rem 1.25rem;
			min-width: 60px;
			min-height: 48px;
			font-size: 1.1rem;
		}
	}

	.btn-adjust:hover:not(:disabled) {
		background: #f8f9fa;
		border-color: #adb5bd;
	}

	.btn-adjust:active:not(:disabled) {
		background: #e9ecef;
	}

	.btn-adjust:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.not-found-message .hint {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		opacity: 0.8;
	}

	.error-message p,
	.success-message p,
	.not-found-message p {
		margin: 0;
	}

	@media (max-width: 768px) {
		.scan-page {
			padding: 0.75rem;
		}

		.scan-page h1 {
			font-size: 1.5rem;
			margin-bottom: 1rem;
		}

		.lookup-form {
			flex-direction: column;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.product-info {
			flex-direction: column;
			align-items: center;
			text-align: center;
			padding: 1rem;
		}

		.product-image img {
			width: 150px;
			height: 150px;
		}

		.inventory-form {
			padding: 1rem;
		}

		.existing-inventory {
			padding: 1rem;
		}

		.inventory-item {
			padding: 1rem;
		}

		/* Größere Touch-Targets */
		.btn-primary,
		.btn-success {
			padding: 1rem 1.5rem;
			font-size: 1.05rem;
			min-height: 48px;
		}

		.btn-adjust {
			padding: 0.75rem 1.25rem;
			min-width: 60px;
			min-height: 48px;
			font-size: 1.1rem;
		}

		.form-group input,
		.form-group select,
		.form-group textarea {
			font-size: 16px; /* Prevents iOS zoom on focus */
			padding: 0.875rem;
		}

		/* Bessere Lesbarkeit */
		.scanner-section h2,
		.manual-section h2 {
			font-size: 1.1rem;
		}

		.status-indicator {
			font-size: 0.95rem;
		}
	}

	@media (max-width: 390px) {
		.scan-page {
			padding: 0.5rem;
		}

		.scan-page h1 {
			font-size: 1.25rem;
			margin-bottom: 0.75rem;
		}

		.scanner-section h2,
		.manual-section h2 {
			font-size: 1rem;
			margin-bottom: 0.75rem;
		}

		.product-info {
			padding: 0.75rem;
		}

		.product-details h3 {
			font-size: 1.1rem;
		}

		.product-image img {
			width: 120px;
			height: 120px;
		}

		.inventory-form,
		.existing-inventory {
			padding: 0.75rem;
		}

		.inventory-form h3,
		.existing-inventory h3 {
			font-size: 1rem;
			margin-bottom: 0.75rem;
		}

		.inventory-item {
			padding: 0.75rem;
		}

		.item-info .location {
			font-size: 0.95rem;
		}

		.btn-adjust {
			padding: 0.65rem 1rem;
			min-width: 55px;
			font-size: 1rem;
		}

		.form-group label {
			font-size: 0.95rem;
		}
	}
</style>
