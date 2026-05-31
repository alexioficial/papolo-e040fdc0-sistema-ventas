<script lang="ts">
  import { onMount } from 'svelte';
  import { clientesApi } from '$lib/api';
  import type { Cliente } from '$lib/types';

  let clientes: Cliente[] = $state([]);
  let loading = $state(true);
  let error = $state('');
  let busqueda = $state('');

  async function cargar() {
    loading = true;
    error = '';
    try {
      clientes = await clientesApi.listar(busqueda || undefined);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(cargar);
</script>

<div class="toolbar">
  <h2>👥 Clientes</h2>
  <a href="/clientes/nuevo" class="btn btn-primary">+ Nuevo Cliente</a>
</div>

<div class="busqueda">
  <input type="text" placeholder="Buscar clientes..." bind:value={busqueda} oninput={cargar} />
</div>

{#if loading}
  <div class="loading">Cargando clientes...</div>
{:else if error}
  <div class="error">{error}</div>
{:else}
  <div class="card">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each clientes as c}
            <tr>
              <td><a href="/clientes/{c._id}">{c.nombre}</a></td>
              <td>{c.email}</td>
              <td>{c.telefono || '-'}</td>
              <td>
                <a href="/clientes/{c._id}" class="btn btn-outline btn-sm">Ver</a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#if clientes.length === 0}
      <p class="text-center text-muted mt">No hay clientes registrados</p>
    {/if}
  </div>
{/if}
