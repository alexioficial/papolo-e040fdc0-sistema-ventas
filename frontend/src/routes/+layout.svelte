<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
</script>

<div class="layout">
  <aside class="sidebar">
    <h1>📊 Ventas</h1>
    <nav>
      <a href="/" class:active={$page.url.pathname === '/'}>
        🏠 Dashboard
      </a>
      <a href="/productos" class:active={$page.url.pathname.startsWith('/productos')}>
        📦 Productos
      </a>
      <a href="/clientes" class:active={$page.url.pathname.startsWith('/clientes')}>
        👥 Clientes
      </a>
      <a href="/ventas" class:active={$page.url.pathname.startsWith('/ventas')}>
        🧾 Ventas
      </a>
      <a href="/carrito" class:active={$page.url.pathname.startsWith('/carrito')}>
        🛒 Carrito
      </a>
    </nav>
  </aside>
  <main class="main-content">
    {@render children()}
  </main>
</div>

<script lang="ts" context="module">
  export const ssr = false;
</script>
