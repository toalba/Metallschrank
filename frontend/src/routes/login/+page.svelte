<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/auth';
	import { api } from '$lib/api';
	
	let username = '';
	let password = '';
	let error = '';
	let loading = false;
	
	async function handleLogin() {
		error = '';
		loading = true;
		
		try {
			// Temporarily set credentials to test them
			auth.login(username, password);
			
			// Verify with backend
			await api.checkAuth();
			
			// Success - redirect to home
			goto('/');
		} catch (e) {
			// Invalid credentials - clear and show error
			auth.logout();
			error = 'Ungültige Anmeldedaten';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login - Metallschrank</title>
</svelte:head>

<div class="login-container">
	<div class="login-card">
		<h1>🔐 Anmelden</h1>
		<p class="subtitle">Metallschrank Inventory</p>
		
		<form on:submit|preventDefault={handleLogin}>
			{#if error}
				<div class="error">{error}</div>
			{/if}
			
			<div class="form-group">
				<label for="username">Benutzername</label>
				<input
					type="text"
					id="username"
					bind:value={username}
					placeholder="admin"
					required
					disabled={loading}
				/>
			</div>
			
			<div class="form-group">
				<label for="password">Passwort</label>
				<input
					type="password"
					id="password"
					bind:value={password}
					placeholder="••••••"
					required
					disabled={loading}
				/>
			</div>
			
			<button type="submit" class="btn-login" disabled={loading}>
				{#if loading}
					Anmelden...
				{:else}
					Anmelden
				{/if}
			</button>
		</form>
	</div>
</div>

<style>
	.login-container {
		min-height: 80vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-lg);
	}
	
	.login-card {
		background: white;
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		padding: var(--spacing-xl);
		width: 100%;
		max-width: 400px;
	}
	
	h1 {
		margin: 0 0 var(--spacing-xs);
		text-align: center;
		color: var(--color-primary);
	}
	
	.subtitle {
		text-align: center;
		color: var(--color-text-light);
		margin: 0 0 var(--spacing-lg);
	}
	
	.form-group {
		margin-bottom: var(--spacing-md);
	}
	
	label {
		display: block;
		margin-bottom: var(--spacing-xs);
		font-weight: 500;
		color: var(--color-text);
	}
	
	input {
		width: 100%;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 1rem;
		transition: border-color 0.2s, box-shadow 0.2s;
	}
	
	input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}
	
	input:disabled {
		background: var(--color-bg);
		cursor: not-allowed;
	}
	
	.btn-login {
		width: 100%;
		padding: var(--spacing-md);
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}
	
	.btn-login:hover:not(:disabled) {
		background: var(--color-primary-dark);
	}
	
	.btn-login:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}
	
	.error {
		background: var(--color-error-bg, #fef2f2);
		color: var(--color-error, #dc2626);
		padding: var(--spacing-sm) var(--spacing-md);
		border-radius: var(--radius-md);
		margin-bottom: var(--spacing-md);
		text-align: center;
	}
</style>
