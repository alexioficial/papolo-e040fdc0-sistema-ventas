<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { productosApi, carritoApi } from '$lib/api';
  import type { Producto } from '$lib/types';

  let producto: Producto | null = $state(null);
  let loading = $state(true);
  let error = $state('');
  let editando = $state(false);
  let saving = $state(false);
  let msg = $state('');
  let cantidad = $state(1);

  // Edición
  let editForm: any = $state({});

  const id = $derived($page.url.pathname.split('/').pop() || '');

  onMount(async () => {
    try {
      producto = await productosApi.obtener(id);
      editForm = { ...producto };
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function guardar() {
    saving = true;
    error = '';
    try {
      producto = await productosApi.actualizar(id, editForm);
      editando = false;
      msg = 'Producto actualizado';
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  async function agregarAlCarrito() {
    try {
      await carritoApi.agregar(id, cantidad);
      msg = `Agregado al carrito (${cantidad})`;
    } catch (e: any) {
      error = e.message;
    }
  }
</script>

<div class="toolbar">
  <h2>Producto</h2>
  <div class="action-buttons">
    <button class="btn btn-outline" onclick={() => editando = !editando}>
      {editando ? 'Cancelar' : '✏️ Editar'}
    </button>
    <a href="/productos" class="btn btn-outline">← Volver</a>
  </div>
</div>

{#if loading}
  <div class="loading">Cargando...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if producto}
  {#if msg}
    <div class="card" style="background: #dcfce7; color: #166534;">{msg}</div>
  {/if}

  {#if editando}
    <div class="card">
      <form onsubmit={(e) => { e.preventDefault(); guardar(); }}>
        <div class="form-row">
          <div class="form-group">
            <label>Nombre</label>
            <input type="text" bind:value={editForm.nombre} />
          </div>
          <div class="form-group">
            <label>SKU</label>
            <input type="text" bind:value={editForm.sku} />
          </div>
        </div>
        <div class="form-group">
          <label>Descripción</label>
          <textarea rows="3" bind:value={editForm.descripcion}></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Precio</label>
            <input type="number" step="0.01" bind:value={editForm.precio} />
          </div>
          <div class="form-group">
            <label>Stock</label>
            <input type="number" bind:value={editForm.stock} />
          </div>
        </div>
        <div class="form-group">
          <label>Categoría</label>
          <select bind:value={editForm.categoria}>
            <option value="General">General</option>
            <option value="Electrónica">Electrónica</option>
            <option value="Ropa">Ropa</option>
            <option value="Alimentos">Alimentos</option>
            <option value="Hogar">Hogar</option>
            <option value="Otros">Otros</option>
          </select>
        </div>
        <div class="mt">
          <button type="submit" class="btn btn-primary" disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </form>
    </div>
  {:else}
    <div class="card">
      <h2>{producto.nombre}</h2>
      <p class="text-muted">SKU: {producto.sku}</p>
      <p>{producto.descripcion || 'Sin descripción'}</p>
      <div class="stats-grid" style="margin-top: 1rem;">
        <div class="stat-card">
          <div class="label">Precio</div>
          <div class="value">${producto.precio.toFixed(2)}</div>
        </div>
        <div class="stat-card">
          <div class="label">Stock</div>
          <div class="value" class:danger={producto.stock < 5}>{producto.stock}</div>
        </div>
        <div class="stat-card">
          <div class="label">Categoría</div>
          <div class="value" style="font-size: 1rem;">{producto.categoria}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Agregar al Carrito</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Cantidad</label>
          <input type="number" min="1" max={producto.stock} bind:value={cantidad} />
        </div>
        <div class="form-group" style="display: flex; align-items: flex-end;">
          <button class="btn btn-success" onclick={agregarAlCarrito} disabled={producto.stock === 0}>
            🛒 Agregar al Carrito
          </button>
        </div>
      </div>
    </div>
  {/if}
{/if}
