<script lang="ts">
	import { onMount, onDestroy, createEventDispatcher } from 'svelte';
	import { BrowserMultiFormatReader } from '@zxing/browser';
	import type { Result } from '@zxing/library';

	const dispatch = createEventDispatcher<{ scan: string }>();

	let videoElement: HTMLVideoElement;
	let codeReader: BrowserMultiFormatReader | null = null;
	let isScanning = false;
	let error: string | null = null;
	let permissionDenied = false;
	let stream: MediaStream | null = null;

	onMount(() => {
		codeReader = new BrowserMultiFormatReader();
	});

	onDestroy(() => {
		stopScanning();
	});

	async function startScanning() {
		if (!codeReader || isScanning) return;

		error = null;
		permissionDenied = false;

		try {
			// Check if getUserMedia is available
			if (!navigator.mediaDevices && !navigator.getUserMedia) {
				error = 'Kamera-API nicht verfügbar. Bitte über HTTPS zugreifen.';
				return;
			}

			// Request camera access with constraints
			const constraints: MediaStreamConstraints = {
				video: {
					facingMode: 'environment' // Prefer back camera on mobile
				}
			};

			// Try modern API first, fallback to legacy
			if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
				stream = await navigator.mediaDevices.getUserMedia(constraints);
			} else {
				// Legacy API fallback
				const getUserMedia = navigator.getUserMedia || 
					(navigator as any).webkitGetUserMedia || 
					(navigator as any).mozGetUserMedia;
				
				stream = await new Promise<MediaStream>((resolve, reject) => {
					getUserMedia.call(navigator, constraints, resolve, reject);
				});
			}

			videoElement.srcObject = stream;
			
			isScanning = true;

			// Start decoding from video element
			await codeReader.decodeFromVideoElement(
				videoElement,
				(result: Result | null, error: Error | undefined) => {
					if (result) {
						const code = result.getText();
						dispatch('scan', code);
						// Optionally stop scanning after successful scan
						// stopScanning();
					}
				}
			);
		} catch (err) {
			isScanning = false;
			if (err instanceof Error) {
				if (err.name === 'NotAllowedError' || err.message.includes('Permission denied')) {
					permissionDenied = true;
					error = 'Kamerazugriff verweigert. Bitte Berechtigung erteilen.';
				} else if (err.name === 'NotFoundError') {
					error = 'Keine Kamera gefunden';
				} else {
					error = `Kamerafehler: ${err.message}`;
				}
			} else {
				error = 'Unbekannter Fehler beim Starten der Kamera';
			}
		}
	}

	function stopScanning() {
		// Stop the media stream tracks
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}

		// Clear video element
		if (videoElement) {
			videoElement.srcObject = null;
		}

		// Reset code reader if it has the method
		if (codeReader && typeof codeReader.reset === 'function') {
			try {
				codeReader.reset();
			} catch (e) {
				// Ignore reset errors
				console.warn('CodeReader reset failed:', e);
			}
		}

		isScanning = false;
	}

	function toggleScanning() {
		if (isScanning) {
			stopScanning();
		} else {
			startScanning();
		}
	}
</script>

<div class="barcode-scanner">
	<div class="video-container">
		<!-- svelte-ignore a11y-media-has-caption -->
		<video bind:this={videoElement} class:active={isScanning}></video>
		{#if !isScanning}
			<div class="video-placeholder">
				<p>Kamera nicht aktiv</p>
			</div>
		{/if}
	</div>

	<div class="controls">
		<button type="button" on:click={toggleScanning} class="btn-primary">
			{isScanning ? 'Kamera stoppen' : 'Kamera starten'}
		</button>
	</div>

	{#if error}
		<div class="error-message">
			<p>{error}</p>
			{#if permissionDenied}
				<p class="hint">
					Bitte erlauben Sie den Kamerazugriff in Ihren Browser-Einstellungen.
				</p>
			{/if}
		</div>
	{/if}
</div>

<style>
	.barcode-scanner {
		width: 100%;
		max-width: 600px;
		margin: 0 auto;
	}

	.video-container {
		position: relative;
		width: 100%;
		aspect-ratio: 4 / 3;
		background: #000;
		border-radius: 8px;
		overflow: hidden;
	}

	video {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: none;
	}

	video.active {
		display: block;
	}

	.video-placeholder {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #999;
	}

	.controls {
		margin-top: 1rem;
		display: flex;
		justify-content: center;
	}

	.btn-primary {
		padding: 0.75rem 1.5rem;
		background: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
		transition: background 0.2s;
	}

	.btn-primary:hover {
		background: #0056b3;
	}

	.btn-primary:active {
		background: #004085;
	}

	.error-message {
		margin-top: 1rem;
		padding: 1rem;
		background: #f8d7da;
		color: #721c24;
		border-radius: 4px;
		border: 1px solid #f5c6cb;
	}

	.error-message p {
		margin: 0;
	}

	.error-message .hint {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		opacity: 0.8;
	}

	/* Mobile optimizations */
	@media (max-width: 640px) {
		.video-container {
			aspect-ratio: 3 / 4;
		}
	}
</style>
