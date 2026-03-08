<script lang="ts">
	import { onMount, onDestroy, createEventDispatcher } from 'svelte';
	import { BrowserMultiFormatReader } from '@zxing/browser';
	import { BarcodeFormat, DecodeHintType } from '@zxing/library';
	import type { Result } from '@zxing/library';

	const dispatch = createEventDispatcher<{ scan: string }>();

	export function stop() {
		stopScanning();
	}

	// Only scan product barcode formats (skip QR, Aztec, DataMatrix etc.)
	const BARCODE_HINTS = new Map<DecodeHintType, any>();
	BARCODE_HINTS.set(DecodeHintType.POSSIBLE_FORMATS, [
		BarcodeFormat.EAN_13,
		BarcodeFormat.EAN_8,
		BarcodeFormat.UPC_A,
		BarcodeFormat.UPC_E,
		BarcodeFormat.CODE_128,
		BarcodeFormat.CODE_39,
	]);
	BARCODE_HINTS.set(DecodeHintType.TRY_HARDER, true);

	let videoElement: HTMLVideoElement;
	let codeReader: BrowserMultiFormatReader | null = null;
	let isScanning = false;
	let scanCooldown = false;
	let lastScannedCode = '';
	let error: string | null = null;
	let permissionDenied = false;
	let stream: MediaStream | null = null;

	const SCAN_COOLDOWN_MS = 2000;

	function createReader(): BrowserMultiFormatReader {
		return new BrowserMultiFormatReader(BARCODE_HINTS, {
			delayBetweenScanAttempts: 100,  // Default is 500ms — scan faster
			delayBetweenScanSuccess: 1000,
		});
	}

	onMount(() => {
		codeReader = createReader();
	});

	onDestroy(() => {
		stopScanning();
	});

	async function startScanning() {
		if (!codeReader || isScanning) return;

		error = null;
		permissionDenied = false;
		lastScannedCode = '';

		try {
			if (!navigator.mediaDevices?.getUserMedia) {
				error = 'Kamera-API nicht verfügbar. Bitte über HTTPS zugreifen.';
				return;
			}

			stream = await navigator.mediaDevices.getUserMedia({
				video: {
					facingMode: 'environment',
					width: { ideal: 1280 },
					height: { ideal: 720 },
				}
			});

			// Apply advanced constraints for faster autofocus (best-effort, ignored if unsupported)
			const [track] = stream.getVideoTracks();
			try {
				await track.applyConstraints({
					advanced: [
						{ focusMode: 'continuous' } as any,
						{ focusDistance: 0.15 } as any,  // ~15cm, typical barcode scan distance
					]
				});
			} catch {
				// Not all browsers/cameras support these — that's fine
			}

			videoElement.srcObject = stream;

			isScanning = true;

			// Start decoding from video element
			await codeReader.decodeFromVideoElement(
				videoElement,
				(result: Result | undefined, _error: Error | undefined) => {
					if (result && !scanCooldown) {
						const code = result.getText();
						// Skip if same code scanned again within cooldown
						if (code === lastScannedCode) return;
						lastScannedCode = code;
						scanCooldown = true;
						dispatch('scan', code);
						// Cooldown prevents rapid duplicate scans
						setTimeout(() => {
							scanCooldown = false;
						}, SCAN_COOLDOWN_MS);
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

		// Re-create code reader to reset internal state
		if (codeReader) {
			codeReader = createReader();
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
