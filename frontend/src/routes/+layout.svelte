<script lang="ts">
  import '../app.css';
  let { children } = $props();
</script>

<div class="layout">
  <aside class="sidebar">
    <h1>📊 Ventas</h1>
    <nav>
      <a href="/">🏠 Dashboard</a>
      <a href="/productos">📦 Productos</a>
      <a href="/clientes">👥 Clientes</a>
      <a href="/ventas">🧾 Ventas</a>
      <a href="/carrito">🛒 Carrito</a>
    </nav>
  </aside>
  <main class="main-content" id="main-content">
    {@render children()}
  </main>
</div>
