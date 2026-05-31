<script lang="ts">
  import { onMount } from 'svelte';
  import { carritoApi, ventasApi } from '$lib/api';
  import type { Carrito } from '$lib/types';
  import { goto } from '$app/navigation';

  let carrito: Carrito | null = $state(null);
  let loading = $state(true);
  let error = $state('');
  let msg = $state('');
  let checkoutLoading = $state(false);

  onMount(async () => {
    try {
      carrito = await carritoApi.obtener();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function cargar() {
    try {
      carrito = await carritoApi.obtener();
    } catch (e: any) {
      error = e.message;
    }
  }

  async function actualizar(producto_id: string, cantidad: number) {
    try {
      carrito = await carritoApi.actualizar(producto_id, cantidad);
    } catch (e: any) {
      error = e.message;
    }
  }

  async function eliminar(producto_id: string) {
    try {
      carrito = await carritoApi.eliminar(producto_id);
    } catch (e: any) {
      error = e.message;
    }
  }

  async function checkout() {
    checkoutLoading = true;
    error = '';
    try {
      const venta = await ventasApi.crear();
      msg = `✅ Venta ${venta.folio} creada exitosamente`;
      carrito = null;
      setTimeout(() => goto(`/ventas/${venta._id}`), 1500);
    } catch (e: any) {
      error = e.message;
    } finally {
      checkoutLoading = false;
    }
  }

  async function limpiar() {
    if (!confirm('¿Vaciar el carrito?')) return;
    try {
      await carritoApi.limpiar();
      carrito = null;
    } catch (e: any) {
      error = e.message;
    }
  }
</script>

<div class="toolbar">
  <h2>🛒 Carrito de Compras</h2>
</div>

{#if msg}
  <div class="card" style="background: #dcfce7; color: #166534;">{msg}</div>
{/if}

{#if loading}
  <div class="loading">Cargando carrito...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if !carrito || carrito.items.length === 0}
  <div class="card text-center">
    <p style="font-size: 1.2rem; padding: 2rem;">🛒 Tu carrito está vacío</p>
    <a href="/productos" class="btn btn-primary">Ir a Productos</a>
  </div>
{:else}
  <div class="card">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Precio</th>
            <th>Cantidad</th>
            <th>Subtotal</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each carrito.items as item}
            <tr>
              <td>{item.producto_nombre}</td>
              <td>${item.precio_unitario.toFixed(2)}</td>
              <td>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <button
                    class="btn btn-outline btn-sm"
                    onclick={() => actualizar(item.producto_id, Math.max(1, item.cantidad - 1))}
                    disabled={item.cantidad <= 1}
                  >−</button>
                  <span><strong>{item.cantidad}</strong></span>
                  <button
                    class="btn btn-outline btn-sm"
                    onclick={() => actualizar(item.producto_id, item.cantidad + 1)}
                  >+</button>
                </div>
              </td>
              <td><strong>${(item.cantidad * item.precio_unitario).toFixed(2)}</strong></td>
              <td>
                <button class="btn btn-danger btn-sm" onclick={() => eliminar(item.producto_id)}>✕</button>
              </td>
            </tr>
          {/each}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" style="text-align: right; font-weight: 700; font-size: 1.1rem;">Total:</td>
            <td><strong style="font-size: 1.3rem;">${carrito.total.toFixed(2)}</strong></td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  <div class="card flex-between">
    <button class="btn btn-outline" onclick={limpiar}>🗑️ Vaciar Carrito</button>
    <button class="btn btn-success" onclick={checkout} disabled={checkoutLoading}>
      {checkoutLoading ? 'Procesando...' : '✅ Realizar Venta'}
    </button>
  </div>
{/if}
