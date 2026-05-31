<script lang="ts">
  import { onMount } from 'svelte';
  import { ventasApi } from '$lib/api';
  import type { DashboardStats } from '$lib/types';

  let stats: DashboardStats | null = $state(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      stats = await ventasApi.stats();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<div class="toolbar">
  <h2>🏠 Dashboard</h2>
</div>

{#if loading}
  <div class="loading">Cargando estadísticas...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if stats}
  <div class="stats-grid">
    <div class="stat-card">
      <div class="label">Ventas Hoy</div>
      <div class="value">{stats.ventas_hoy}</div>
    </div>
    <div class="stat-card">
      <div class="label">Total Ventas Hoy</div>
      <div class="value success">${stats.total_ventas_hoy.toFixed(2)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Clientes Registrados</div>
      <div class="value">{stats.total_clientes}</div>
    </div>
    <div class="stat-card">
      <div class="label">Productos Activos</div>
      <div class="value">{stats.total_productos}</div>
    </div>
    <div class="stat-card">
      <div class="label">Productos Bajo Stock</div>
      <div class="value warning">{stats.productos_bajo_stock}</div>
    </div>
    <div class="stat-card">
      <div class="label">Ventas Totales</div>
      <div class="value success">${stats.ventas_totales.toFixed(2)}</div>
    </div>
  </div>

  {#if stats.top_productos.length > 0}
    <div class="card">
      <h2>🏆 Top 5 Productos Más Vendidos</h2>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>Cantidad Vendida</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {#each stats.top_productos as p}
              <tr>
                <td>{p.nombre}</td>
                <td>{p.cantidad}</td>
                <td>${p.total.toFixed(2)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
{/if}
