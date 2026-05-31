<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { ventasApi } from '$lib/api';
  import type { Venta } from '$lib/types';

  let venta: Venta | null = $state(null);
  let loading = $state(true);
  let error = $state('');
  let msg = $state('');

  const id = $derived($page.url.pathname.split('/').pop() || '');

  onMount(async () => {
    try {
      venta = await ventasApi.obtener(id);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function cancelar() {
    if (!confirm('¿Cancelar esta venta? Se restaurará el stock.')) return;
    try {
      venta = await ventasApi.cancelar(id);
      msg = 'Venta cancelada exitosamente';
    } catch (e: any) {
      error = e.message;
    }
  }
</script>

<div class="toolbar">
  <h2>Venta</h2>
  <a href="/ventas" class="btn btn-outline">← Volver</a>
</div>

{#if loading}
  <div class="loading">Cargando...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if venta}
  {#if msg}
    <div class="card" style="background: #dcfce7; color: #166534;">{msg}</div>
  {/if}

  <div class="card">
    <div class="flex-between">
      <div>
        <h2>{venta.folio}</h2>
        <p class="text-muted">{new Date(venta.fecha).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
      </div>
      <div>
        {#if venta.estado === 'completada'}
          <span class="badge badge-success" style="font-size: 1rem; padding: 0.25rem 1rem;">Completada</span>
        {:else}
          <span class="badge badge-danger" style="font-size: 1rem; padding: 0.25rem 1rem;">Cancelada</span>
        {/if}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Items</h2>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Precio Unitario</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {#each venta.items as item}
            <tr>
              <td>{item.producto_nombre}</td>
              <td>{item.cantidad}</td>
              <td>${item.precio_unitario.toFixed(2)}</td>
              <td><strong>${item.subtotal.toFixed(2)}</strong></td>
            </tr>
          {/each}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" style="text-align: right; font-weight: 700;">Total:</td>
            <td><strong style="font-size: 1.2rem;">${venta.total.toFixed(2)}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  {#if venta.estado === 'completada'}
    <div class="card">
      <button class="btn btn-danger" onclick={cancelar}>
        Cancelar Venta
      </button>
      <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.85rem;">
        Se restaurará el stock de todos los productos de esta venta.
      </p>
    </div>
  {/if}
{/if}
