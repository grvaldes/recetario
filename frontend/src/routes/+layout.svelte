<script lang="ts">
	import '../app.css';
	import Navbar from '#lib/components/Navbar.svelte';
	import Footer from '#lib/components/Footer.svelte';
	import { healthStore } from '#lib/stores/health';
	import type { LayoutProps } from './$types';


	let { children }: LayoutProps = $props();

	let env = $derived($healthStore.data?.environment ?? 'loading');
	let version = $derived($healthStore.data?.version ?? '0.1.0');
</script>

<svelte:head>
	<title>Recetario &bull; Recipe Management</title>
</svelte:head>

<div class="app-shell">
	<Navbar environment={env} {version} />
	<main class="app-main">
		{@render children()}
	</main>
	<Footer />
</div>

<style>
	.app-shell {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.app-main {
		flex: 1;
		width: 100%;
		max-width: var(--container-max);
		margin: 0 auto;
		padding: 2rem 1.5rem 3rem;
	}
</style>
