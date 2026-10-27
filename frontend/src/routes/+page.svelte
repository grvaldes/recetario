<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import StatusBadge from '#lib/components/StatusBadge.svelte';
	import ComponentCard from '#lib/components/ComponentCard.svelte';
	import MetricCard from '#lib/components/MetricCard.svelte';
	import { healthStore } from '#lib/stores/health';


	let autoRefresh = $state(true);
	let refreshInterval: ReturnType<typeof setInterval> | null = null;

	onMount(() => {
		healthStore.check();
		setupInterval();
	});

	onDestroy(() => {
		clearIntervalTimer();
	});

	function setupInterval() {
		clearIntervalTimer();
		if (autoRefresh) {
			refreshInterval = setInterval(() => {
				healthStore.check();
			}, 10000);
		}
	}

	function clearIntervalTimer() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}
	}

	function toggleAutoRefresh() {
		autoRefresh = !autoRefresh;
		if (autoRefresh) {
			healthStore.check();
			setupInterval();
		} else {
			clearIntervalTimer();
		}
	}

	function handleManualRefresh() {
		healthStore.check();
	}

	const overallStatus = $derived($healthStore.data?.status ?? ($healthStore.error ? 'down' : 'degraded'));
	const dbDetails = $derived($healthStore.data?.components?.database);
	const storageDetails = $derived($healthStore.data?.components?.uploads_storage);

	function formatUtcDate(dateStr?: string): string {
		if (!dateStr) return 'Pending...';
		try {
			const d = new Date(dateStr);
			return d.toUTCString();
		} catch {
			return dateStr;
		}
	}
</script>

<svelte:head>
	<title>System Status & Diagnostics &bull; Recetario</title>
	<meta name="description" content="Recetario application status dashboard and system diagnostics." />
</svelte:head>

<section class="dashboard">
	<!-- Hero Header -->
	<header class="dashboard-header">
		<div class="header-content">
			<span class="subheading">Self-Hosted Recipe Platform</span>
			<h1 class="main-title">System Status & Diagnostics</h1>
			<p class="description">
				Real-time health telemetry across the modular monolith foundation, including PostgreSQL database connectivity, persistent storage, and API routing.
			</p>
		</div>

		<div class="header-controls">
			<button
				id="btn-auto-refresh"
				class="btn-toggle {autoRefresh ? 'active' : ''}"
				onclick={toggleAutoRefresh}
				title="Toggle automatic polling every 10 seconds"
			>
				<span class="indicator-dot"></span>
				Auto-Refresh: {autoRefresh ? 'ON' : 'OFF'}
			</button>

			<button
				id="btn-refresh"
				class="btn-primary"
				onclick={handleManualRefresh}
				disabled={$healthStore.loading}
				aria-label="Refresh application status"
			>
				<span class="icon {$healthStore.loading ? 'spinning' : ''}" aria-hidden="true">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
						<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
						<path d="M3 3v5h5" />
						<path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
						<path d="M16 21h5v-5" />
					</svg>
				</span>
				<span>{$healthStore.loading ? 'Checking...' : 'Refresh Status'}</span>
			</button>
		</div>
	</header>

	<!-- Status Banner -->
	<div class="status-banner {overallStatus}" id="system-status-banner">
		<div class="banner-left">
			<span class="banner-label">Overall System Health:</span>
			<div id="health-status-badge">
				<StatusBadge status={overallStatus} size="lg" />
			</div>
		</div>

		{#if $healthStore.lastChecked}
			<div class="banner-right">
				<span class="last-checked">
					Last verified: {$healthStore.lastChecked.toLocaleTimeString()}
				</span>
			</div>
		{/if}
	</div>

	<!-- Error Alert if Connection Fails -->
	{#if $healthStore.error}
		<div class="alert-error" id="api-error-alert" role="alert">
			<div class="alert-icon" aria-hidden="true">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10" />
					<line x1="12" y1="8" x2="12" y2="12" />
					<line x1="12" y1="16" x2="12.01" y2="16" />
				</svg>
			</div>
			<div class="alert-content">
				<strong>Communication Error:</strong>
				<span>{$healthStore.error}</span>
				<p class="alert-hint">
					Ensure backend service is running and accessible via <code>GET /api/health</code>.
				</p>
			</div>
		</div>
	{/if}

	<!-- Backing Components Grid -->
	<section class="section-components">
		<h2 class="section-title">Backing Infrastructure Services</h2>
		<div class="grid-components">
			<ComponentCard
				name="PostgreSQL Database"
				type="database"
				status={dbDetails?.status ?? ($healthStore.loading ? 'degraded' : 'down')}
				message={dbDetails?.message ?? ($healthStore.loading ? 'Checking connection...' : 'Unreachable')}
				details="SQLAlchemy 2.x Session Pool & Alembic Migrations"
			/>

			<ComponentCard
				name="Recipe Storage"
				type="storage"
				status={storageDetails?.status ?? ($healthStore.loading ? 'degraded' : 'down')}
				message={storageDetails?.message ?? ($healthStore.loading ? 'Validating disk access...' : 'Inaccessible')}
				details="Configurable Persistent Volume for Media Uploads"
			/>

			<ComponentCard
				name="FastAPI Core Engine"
				type="core"
				status={$healthStore.data ? 'operational' : ($healthStore.loading ? 'degraded' : 'down')}
				message={$healthStore.data ? `Responding on /api prefix (v${$healthStore.data.version})` : 'Awaiting connection...'}
				details="Pydantic v2 Validation & Dependency Injection"
			/>
		</div>
	</section>

	<!-- Telemetry Metrics Grid -->
	<section class="section-metrics">
		<h2 class="section-title">Backend Metadata & UTC Telemetry</h2>
		<div class="grid-metrics">
			<MetricCard
				id="metric-version"
				label="Application Version"
				value={$healthStore.data?.version ?? '0.1.0'}
				caption="Semantic versioning"
			/>

			<MetricCard
				id="metric-environment"
				label="Active Environment"
				value={$healthStore.data?.environment ?? 'development'}
				caption="Configured via environment variables"
			/>

			<MetricCard
				id="metric-timestamp"
				label="Server UTC Timestamp"
				value={formatUtcDate($healthStore.data?.timestamp)}
				caption="Timezone-aware UTC standard"
			/>

			<MetricCard
				id="metric-architecture"
				label="Architecture Pattern"
				value="Modular Monolith"
				caption="Clean separation of concerns"
			/>
		</div>
	</section>

	<!-- Foundation Architecture Checklist -->
	<section class="section-checklist">
		<div class="card-checklist">
			<div class="checklist-header">
				<h3 class="checklist-title">Architectural Foundation Checklist</h3>
				<span class="checklist-tag">Initial Scope Verified</span>
			</div>
			<div class="checklist-grid">
				<div class="checklist-item">
					<span class="check-icon" aria-hidden="true">✓</span>
					<div class="check-text">
						<strong>Backend Separation of Concerns</strong>
						<p>HTTP routing, Pydantic schemas, SQLAlchemy models, service business logic, and dependency injection.</p>
					</div>
				</div>
				<div class="checklist-item">
					<span class="check-icon" aria-hidden="true">✓</span>
					<div class="check-text">
						<strong>Frontend Component Isolation</strong>
						<p>Typed API client abstraction, shared TypeScript definitions, presentation components, and SvelteKit routing.</p>
					</div>
				</div>
				<div class="checklist-item">
					<span class="check-icon" aria-hidden="true">✓</span>
					<div class="check-text">
						<strong>Web Server Reverse Proxy</strong>
						<p>Nginx web server serves production frontend build and proxies <code>/api/*</code> requests directly to FastAPI.</p>
					</div>
				</div>
				<div class="checklist-item">
					<span class="check-icon" aria-hidden="true">✓</span>
					<div class="check-text">
						<strong>Security & Persistence</strong>
						<p>PostgreSQL hidden from public ports; persistent Docker volumes for database data and recipe media storage.</p>
					</div>
				</div>
			</div>
		</div>
	</section>
</section>

<style>
	.dashboard {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		animation: fadeIn 0.3s ease-out;
	}

	.dashboard-header {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		border-bottom: 1px solid var(--border-subtle);
		padding-bottom: 1.75rem;
	}

	@media (min-width: 768px) {
		.dashboard-header {
			flex-direction: row;
			align-items: flex-end;
			justify-content: space-between;
		}
	}

	.subheading {
		font-family: var(--font-heading);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-size: 0.8rem;
		font-weight: 700;
		color: var(--brand-primary);
	}

	.main-title {
		font-size: 2.25rem;
		letter-spacing: -0.03em;
		margin: 0.25rem 0 0.5rem;
	}

	.description {
		color: var(--text-secondary);
		max-width: 620px;
		font-size: 1rem;
		line-height: 1.5;
	}

	.header-controls {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	.btn-toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		padding: 0.55rem 0.85rem;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-subtle);
		background: var(--bg-surface);
		color: var(--text-secondary);
		font-size: 0.8rem;
		font-weight: 600;
		transition: all 0.15s ease;
	}

	.btn-toggle.active {
		border-color: var(--brand-sage);
		color: var(--brand-sage);
		background: var(--brand-sage-light);
	}

	.indicator-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: currentColor;
	}

	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 1.15rem;
		border-radius: var(--radius-sm);
		background: var(--brand-primary);
		color: #ffffff;
		font-weight: 600;
		font-size: 0.875rem;
		box-shadow: var(--shadow-sm);
		transition: all 0.2s ease;
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--brand-primary-hover);
		transform: translateY(-1px);
		box-shadow: var(--shadow-md);
	}

	.btn-primary:disabled {
		opacity: 0.65;
		cursor: not-allowed;
	}

	.icon.spinning {
		animation: spin 1s linear infinite;
	}

	/* Status Banner */
	.status-banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1.5rem;
		border-radius: var(--radius-md);
		border: 1px solid var(--border-subtle);
		background: var(--bg-surface);
		box-shadow: var(--shadow-sm);
	}

	.status-banner.operational {
		border-left: 5px solid var(--status-operational);
	}

	.status-banner.degraded {
		border-left: 5px solid var(--status-degraded);
	}

	.status-banner.down {
		border-left: 5px solid var(--status-down);
	}

	.banner-left {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.banner-label {
		font-family: var(--font-heading);
		font-weight: 600;
		font-size: 1.05rem;
		color: var(--text-primary);
	}

	.last-checked {
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	/* Alert */
	.alert-error {
		display: flex;
		gap: 0.85rem;
		background: var(--status-down-bg);
		border: 1px solid var(--status-down-border);
		color: var(--status-down);
		padding: 1rem 1.25rem;
		border-radius: var(--radius-md);
	}

	.alert-content strong {
		display: block;
		margin-bottom: 0.2rem;
	}

	.alert-hint {
		margin-top: 0.4rem;
		font-size: 0.825rem;
		opacity: 0.9;
	}

	.alert-hint code {
		background: rgba(0, 0, 0, 0.08);
		padding: 0.15rem 0.35rem;
		border-radius: var(--radius-sm);
	}

	/* Section Headings */
	.section-title {
		font-size: 1.25rem;
		margin-bottom: 1rem;
		letter-spacing: -0.01em;
	}

	/* Grids */
	.grid-components {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}

	@media (min-width: 768px) {
		.grid-components {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	.grid-metrics {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}

	@media (min-width: 600px) {
		.grid-metrics {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (min-width: 992px) {
		.grid-metrics {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	/* Checklist Card */
	.card-checklist {
		background: var(--bg-surface);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
	}

	.checklist-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1.25rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid var(--border-subtle);
	}

	.checklist-title {
		font-size: 1.1rem;
	}

	.checklist-tag {
		background: var(--brand-sage-light);
		color: var(--brand-sage);
		border: 1px solid var(--brand-sage);
		padding: 0.2rem 0.6rem;
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		font-weight: 600;
	}

	.checklist-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}

	@media (min-width: 768px) {
		.checklist-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	.checklist-item {
		display: flex;
		gap: 0.75rem;
		align-items: flex-start;
	}

	.check-icon {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		background: var(--status-operational-bg);
		color: var(--status-operational);
		font-size: 0.85rem;
		font-weight: 700;
		flex-shrink: 0;
		margin-top: 2px;
	}

	.check-text strong {
		font-size: 0.925rem;
		color: var(--text-primary);
		display: block;
	}

	.check-text p {
		font-size: 0.825rem;
		color: var(--text-secondary);
		margin-top: 0.2rem;
		line-height: 1.4;
	}
</style>
