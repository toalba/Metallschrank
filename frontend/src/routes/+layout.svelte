<script lang="ts">
	import '../app.css';
</script>

<div class="app">
	<header>
		<nav class="container">
			<div class="nav-content">
				<h1 class="logo">📦 Metallschrank</h1>
				<div class="nav-links">
					<a href="/">Home</a>
					<a href="/scan">Scan</a>
					<a href="/inventory">Inventory</a>
				</div>
			</div>
		</nav>
	</header>

	<main class="container">
		<slot />
	</main>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	header {
		background-color: var(--color-primary);
		color: white;
		padding: var(--spacing-md) 0;
		box-shadow: var(--shadow-md);
	}

	.nav-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.logo {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 700;
	}

	.nav-links {
		display: flex;
		gap: var(--spacing-lg);
	}

	.nav-links a {
		color: white;
		text-decoration: none;
		font-weight: 500;
		transition: opacity 0.2s;
	}

	.nav-links a:hover {
		opacity: 0.8;
	}

	main {
		flex: 1;
		padding-top: var(--spacing-xl);
		padding-bottom: var(--spacing-xl);
	}

	@media (max-width: 768px) {
		header {
			padding: 0.75rem 0;
		}

		.logo {
			font-size: 1.1rem;
		}

		.nav-links {
			gap: 0.75rem;
			font-size: 0.9rem;
		}

		.nav-links a {
			padding: 0.25rem 0.5rem;
		}

		main {
			padding-top: 1rem;
			padding-bottom: 1rem;
		}
	}

	@media (max-width: 390px) {
		header {
			padding: 0.5rem 0;
		}

		.nav-content {
			padding: 0 0.5rem;
		}

		.logo {
			font-size: 0.95rem;
		}

		.nav-links {
			gap: 0.5rem;
			font-size: 0.85rem;
		}

		.nav-links a {
			padding: 0.2rem 0.35rem;
		}
	}
</style>
