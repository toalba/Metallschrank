<script lang="ts">
	import '../app.css';
	import { auth } from '$lib/auth';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	
	// Reactive: check if current page is login
	$: isLoginPage = $page.url.pathname === '/login';
	
	// Redirect to login if not authenticated (except on login page)
	$: if (!$auth.isAuthenticated && !isLoginPage && typeof window !== 'undefined') {
		goto('/login');
	}
	
	function handleLogout() {
		auth.logout();
		goto('/login');
	}
</script>

<div class="app">
	{#if $auth.isAuthenticated || isLoginPage}
		{#if !isLoginPage}
			<header>
				<nav class="container">
					<div class="nav-content">
						<a href="/" class="logo">📦 <span class="logo-text">Metallschrank</span></a>
						<div class="nav-links">
							<a href="/scan">Scan</a>
							<a href="/inventory">Inventar</a>
							<button class="logout-btn" on:click={handleLogout} title="Logout ({$auth.username})">
								🚪
							</button>
						</div>
					</div>
				</nav>
			</header>
		{/if}

		<main class="container" class:no-header={isLoginPage}>
			<slot />
		</main>
	{/if}
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
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.nav-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.5rem;
	}

	.logo {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 700;
		color: white;
		text-decoration: none;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		flex-shrink: 0;
	}

	.logo:hover {
		opacity: 0.9;
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
	}

	.nav-links a {
		color: white;
		text-decoration: none;
		font-weight: 500;
		transition: opacity 0.2s;
		white-space: nowrap;
	}

	.nav-links a:hover {
		opacity: 0.8;
	}

	main {
		flex: 1;
		padding-top: var(--spacing-xl);
		padding-bottom: var(--spacing-xl);
	}

	main.no-header {
		padding-top: 0;
	}

	.logout-btn {
		background: rgba(255, 255, 255, 0.2);
		border: 1px solid rgba(255, 255, 255, 0.3);
		color: white;
		padding: 0.4rem 0.6rem;
		border-radius: var(--radius-md);
		cursor: pointer;
		font-size: 1.1rem;
		transition: background 0.2s;
		line-height: 1;
	}

	.logout-btn:hover {
		background: rgba(255, 255, 255, 0.3);
	}

	@media (max-width: 768px) {
		header {
			padding: 0.5rem 0;
		}

		.logo {
			font-size: 1.1rem;
		}

		.logo-text {
			display: none;
		}

		.nav-links {
			gap: 0.75rem;
			font-size: 0.95rem;
		}

		main {
			padding-top: 1rem;
			padding-bottom: 1rem;
		}
	}

	@media (min-width: 769px) {
		.logo-text {
			display: inline;
		}
	}
</style>
