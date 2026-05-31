<script lang="ts">
  import { goto } from '$app/navigation';
  import { clientesApi } from '$lib/api';
  import type { ClienteCreate } from '$lib/types';

  let form: ClienteCreate = $state({
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
  });
  let error = $state('');
  let saving = $state(false);

  async function guardar() {
    saving = true;
    error = '';
    try {
      const creado = await clientesApi.crear(form);
      goto(`/clientes/${creado._id}`);
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>

<div class="toolbar">
  <h2>Nuevo Cliente</h2>
  <a href="/clientes" class="btn btn-outline">← Volver</a>
</div>

<div class="card">
  {#if error}<div class="error">{error}</div>{/if}
  <form onsubmit={(e) => { e.preventDefault(); guardar(); }}>
    <div class="form-group">
      <label>Nombre *</label>
      <input type="text" bind:value={form.nombre} required />
    </div>
    <div class="form-group">
      <label>Email *</label>
      <input type="email" bind:value={form.email} required />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Teléfono</label>
        <input type="text" bind:value={form.telefono} />
      </div>
      <div class="form-group">
        <label>Dirección</label>
        <input type="text" bind:value={form.direccion} />
      </div>
    </div>
    <div class="mt">
      <button type="submit" class="btn btn-primary" disabled={saving}>
        {saving ? 'Guardando...' : 'Guardar Cliente'}
      </button>
    </div>
  </form>
</div>
