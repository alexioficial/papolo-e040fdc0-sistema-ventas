<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { clientesApi } from '$lib/api';
  import type { Cliente, Venta } from '$lib/types';

  let cliente: Cliente | null = $state(null);
  let ventas: Venta[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  const id = $derived($page.url.pathname.split('/').pop() || '');

  onMount(async () => {
    try {
      const [c, v] = await Promise.all([
        clientesApi.obtener(id),
        clientesApi.ventas(id),
      ]);
      cliente = c;
      ventas = v;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<div class="toolbar">
  <h2>Cliente</h2>
  <a href="/clientes" class="btn btn-outline">← Volver</a>
</div>

{#if loading}
  <div class="loading">Cargando...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if cliente}
  <div class="card">
    <h2>{cliente.nombre}</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Email</div>
        <div class="value" style="font-size: 1rem;">{cliente.email}</div>
      </div>
      <div class="stat-card">
        <div class="label">Teléfono</div>
        <div class="value" style="font-size: 1rem;">{cliente.telefono || '-'}</div>
      </div>
      <div class="stat-card">
        <div class="label">Dirección</div>
        <div class="value" style="font-size: 1rem;">{cliente.direccion || '-'}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Historial de Compras</h2>
    {#if ventas.length === 0}
      <p class="text-muted">Este cliente no tiene compras registradas</p>
    {:else}
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
                <td>{v.folio}</td>
                <td>{new Date(v.fecha).toLocaleDateString()}</td>
                <td>{v.items.length}</td>
                <td>${v.total.toFixed(2)}</td>
                <td>
                  {#if v.estado === 'completada'}
                    <span class="badge badge-success">Completada</span>
                  {:else}
                    <span class="badge badge-danger">Cancelada</span>
                  {/if}
                </td>
                <td><a href="/ventas/{v._id}" class="btn btn-outline btn-sm">Ver</a></td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}
