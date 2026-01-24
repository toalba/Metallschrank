<script lang="ts">
	// Home page
</script>

<div class="home">
	<div class="hero">
		<h1>Willkommen zum Metallschrank Inventory System</h1>
		<p>Barcode-basiertes Inventarverwaltungssystem für Ihre Vorräte</p>
		<div class="actions">
			<a href="/scan" class="btn btn-primary">Barcode scannen</a>
			<a href="/inventory" class="btn btn-secondary">Inventar anzeigen</a>
		</div>
	</div>

	<div class="features">
		<div class="card">
			<h3>📱 Barcode-Scan</h3>
			<p>Nutzen Sie Ihre Smartphone-Kamera, um Barcodes zu scannen</p>
		</div>
		<div class="card">
			<h3>🔍 Produktsuche</h3>
			<p>Automatische Suche in lokaler Datenbank und OpenFoodFacts</p>
		</div>
		<div class="card">
			<h3>📍 Standortverwaltung</h3>
			<p>Verfolgen Sie, wo Ihre Artikel im Schrank aufbewahrt werden</p>
		</div>
	</div>
</div>

<style>
	.home {
		max-width: 900px;
		margin: 0 auto;
	}

	.hero {
		text-align: center;
		margin-bottom: var(--spacing-xl);
	}

	.hero h1 {
		font-size: 2.5rem;
		margin-bottom: var(--spacing-md);
		color: var(--color-primary);
	}

	.hero p {
		font-size: 1.25rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-xl);
	}

	.actions {
		display: flex;
		gap: var(--spacing-md);
		justify-content: center;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: var(--spacing-lg);
		margin-top: var(--spacing-xl);
	}

	.features .card {
		text-align: center;
	}

	.features h3 {
		font-size: 1.5rem;
		margin-bottom: var(--spacing-sm);
	}

	.features p {
		color: var(--color-text-light);
	}

	@media (max-width: 768px) {
		.home {
			padding: 0 0.75rem;
		}

		.hero {
			margin-bottom: 2rem;
		}

		.hero h1 {
			font-size: 1.5rem;
			margin-bottom: 0.75rem;
			line-height: 1.3;
		}

		.hero p {
			font-size: 1rem;
			margin-bottom: 1.5rem;
		}

		.actions {
			flex-direction: column;
			gap: 0.75rem;
			width: 100%;
		}

		.actions .btn {
			width: 100%;
			padding: 1rem;
			font-size: 1.05rem;
		}

		.features {
			grid-template-columns: 1fr;
			gap: 1rem;
			margin-top: 2rem;
		}

		.features .card {
			padding: 1rem;
		}

		.features h3 {
			font-size: 1.25rem;
		}

		.features p {
			font-size: 0.95rem;
		}
	}

	@media (max-width: 390px) {
		.home {
			padding: 0 0.5rem;
		}

		.hero {
			margin-bottom: 1.5rem;
		}

		.hero h1 {
			font-size: 1.25rem;
			margin-bottom: 0.5rem;
			line-height: 1.25;
		}

		.hero p {
			font-size: 0.9rem;
			margin-bottom: 1.25rem;
			line-height: 1.4;
		}

		.actions .btn {
			padding: 0.875rem;
			font-size: 1rem;
		}

		.features {
			gap: 0.75rem;
			margin-top: 1.5rem;
		}

		.features .card {
			padding: 0.75rem;
		}

		.features h3 {
			font-size: 1.1rem;
			margin-bottom: 0.5rem;
		}

		.features p {
			font-size: 0.875rem;
			line-height: 1.4;
		}
	}
</style>
