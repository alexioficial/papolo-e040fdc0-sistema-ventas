<script lang="ts">
  import { onMount } from 'svelte';
  import { ventasApi } from '$lib/api';
  import type { Venta } from '$lib/types';

  let ventas: Venta[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      ventas = await ventasApi.listar();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<div class="toolbar">
  <h2>🧾 Ventas</h2>
</div>

{#if loading}
  <div class="loading">Cargando ventas...</div>
{:else if error}
  <div class="error">{error}</div>
{:else}
  <div class="card">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Folio</th>
            <th>Fecha</th>
            <th>Items</th>
            <th>Total</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each ventas as v}
            <tr>
              <td><strong>{v.folio}</strong></td>
              <td>{new Date(v.fecha).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
              <td>{v.items.length}</td>
              <td><strong>${v.total.toFixed(2)}</strong></td>
              <td>
                {#if v.estado === 'completada'}
                  <span class="badge badge-success">Completada</span>
                {:else}
                  <span class="badge badge-danger">Cancelada</span>
                {/if}
              </td>
              <td><a href="/ventas/{v._id}" class="btn btn-outline btn-sm">Detalle</a></td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#if ventas.length === 0}
      <p class="text-center text-muted mt">No hay ventas registradas</p>
    {/if}
  </div>
{/if}
