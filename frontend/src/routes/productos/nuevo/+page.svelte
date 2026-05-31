<script lang="ts">
  import { goto } from '$app/navigation';
  import { productosApi } from '$lib/api';
  import type { ProductoCreate } from '$lib/types';

  let form: ProductoCreate = $state({
    nombre: '',
    descripcion: '',
    precio: 0,
    sku: '',
    stock: 0,
    categoria: 'General',
  });
  let error = $state('');
  let saving = $state(false);

  async function guardar() {
    saving = true;
    error = '';
    try {
      const creado = await productosApi.crear(form);
      goto(`/productos/${creado._id}`);
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>

<div class="toolbar">
  <h2>Nuevo Producto</h2>
  <a href="/productos" class="btn btn-outline">← Volver</a>
</div>

<div class="card">
  {#if error}<div class="error">{error}</div>{/if}
  <form onsubmit={(e) => { e.preventDefault(); guardar(); }}>
    <div class="form-row">
      <div class="form-group">
        <label>Nombre *</label>
        <input type="text" bind:value={form.nombre} required />
      </div>
      <div class="form-group">
        <label>SKU *</label>
        <input type="text" bind:value={form.sku} required />
      </div>
    </div>
    <div class="form-group">
      <label>Descripción</label>
      <textarea rows="3" bind:value={form.descripcion}></textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Precio *</label>
        <input type="number" step="0.01" min="0.01" bind:value={form.precio} required />
      </div>
      <div class="form-group">
        <label>Stock</label>
        <input type="number" min="0" bind:value={form.stock} />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Categoría</label>
        <select bind:value={form.categoria}>
          <option value="General">General</option>
          <option value="Electrónica">Electrónica</option>
          <option value="Ropa">Ropa</option>
          <option value="Alimentos">Alimentos</option>
          <option value="Hogar">Hogar</option>
          <option value="Otros">Otros</option>
        </select>
      </div>
      <div class="form-group">
        <label>URL Imagen</label>
        <input type="text" bind:value={form.imagen_url} placeholder="https://..." />
      </div>
    </div>
    <div class="mt">
      <button type="submit" class="btn btn-primary" disabled={saving}>
        {saving ? 'Guardando...' : 'Guardar Producto'}
      </button>
    </div>
  </form>
</div>
