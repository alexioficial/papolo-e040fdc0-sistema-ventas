<script lang="ts">
  import { onMount } from 'svelte';
  import { productosApi } from '$lib/api';
  import type { Producto } from '$lib/types';

  let productos: Producto[] = $state([]);
  let loading = $state(true);
  let error = $state('');
  let busqueda = $state('');
  let categoria = $state('');

  async function cargar() {
    loading = true;
    error = '';
    try {
      productos = await productosApi.listar({ busqueda: busqueda || undefined, categoria: categoria || undefined });
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(cargar);

  function eliminar(id: string) {
    if (!confirm('¿Desactivar este producto?')) return;
    productosApi.eliminar(id).then(() => cargar());
  }
</script>

<div class="toolbar">
  <h2>📦 Productos</h2>
  <a href="/productos/nuevo" class="btn btn-primary">+ Nuevo Producto</a>
</div>

<div class="busqueda">
  <input type="text" placeholder="Buscar productos..." bind:value={busqueda} oninput={cargar} />
</div>

{#if loading}
  <div class="loading">Cargando productos...</div>
{:else if error}
  <div class="error">{error}</div>
{:else}
  <div class="card">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Precio</th>
            <th>Stock</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each productos as p}
            <tr>
              <td>{p.sku}</td>
              <td><a href="/productos/{p._id}">{p.nombre}</a></td>
              <td><span class="badge badge-success">{p.categoria}</span></td>
              <td>${p.precio.toFixed(2)}</td>
              <td>
                {#if p.stock < 5}
                  <span class="badge badge-warning">{p.stock}</span>
                {:else}
                  {p.stock}
                {/if}
              </td>
              <td class="action-buttons">
                <a href="/productos/{p._id}" class="btn btn-outline btn-sm">Editar</a>
                <button class="btn btn-danger btn-sm" onclick={() => eliminar(p._id)}>Desactivar</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#if productos.length === 0}
      <p class="text-center text-muted mt">No hay productos registrados</p>
    {/if}
  </div>
{/if}
