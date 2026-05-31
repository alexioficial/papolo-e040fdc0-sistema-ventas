import type {
  Producto, ProductoCreate, ProductoUpdate,
  Cliente, ClienteCreate,
  Venta,
  Carrito, CarritoItem,
  DashboardStats,
} from './types';

const BASE = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (res.status === 204) return undefined as T;
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`);
  }
  return data as T;
}

// -- Productos --
export const productosApi = {
  listar: (params?: { categoria?: string; busqueda?: string }) => {
    const q = new URLSearchParams();
    if (params?.categoria) q.set('categoria', params.categoria);
    if (params?.busqueda) q.set('busqueda', params.busqueda);
    const qs = q.toString();
    return request<Producto[]>(`/productos${qs ? `?${qs}` : ''}`);
  },
  obtener: (id: string) => request<Producto>(`/productos/${id}`),
  crear: (data: ProductoCreate) =>
    request<Producto>('/productos', { method: 'POST', body: JSON.stringify(data) }),
  actualizar: (id: string, data: ProductoUpdate) =>
    request<Producto>(`/productos/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  eliminar: (id: string) =>
    request<void>(`/productos/${id}`, { method: 'DELETE' }),
  ajustarStock: (id: string, stock: number) =>
    request<Producto>(`/productos/${id}/stock`, { method: 'PATCH', body: JSON.stringify({ stock }) }),
};

// -- Clientes --
export const clientesApi = {
  listar: (busqueda?: string) => {
    const q = busqueda ? `?busqueda=${encodeURIComponent(busqueda)}` : '';
    return request<Cliente[]>(`/clientes${q}`);
  },
  obtener: (id: string) => request<Cliente>(`/clientes/${id}`),
  crear: (data: ClienteCreate) =>
    request<Cliente>('/clientes', { method: 'POST', body: JSON.stringify(data) }),
  actualizar: (id: string, data: Partial<ClienteCreate>) =>
    request<Cliente>(`/clientes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  eliminar: (id: string) =>
    request<void>(`/clientes/${id}`, { method: 'DELETE' }),
  ventas: (id: string) => request<Venta[]>(`/clientes/${id}/ventas`),
};

// -- Carrito --
function getSesionId(): string {
  let id = sessionStorage.getItem('sesion_id');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('sesion_id', id);
  }
  return id;
}

export const carritoApi = {
  obtener: () => request<Carrito>(`/carrito/${getSesionId()}`),
  agregar: (producto_id: string, cantidad: number) =>
    request<Carrito>(`/carrito/${getSesionId()}/items`, {
      method: 'POST',
      body: JSON.stringify({ producto_id, cantidad }),
    }),
  actualizar: (producto_id: string, cantidad: number) =>
    request<Carrito>(`/carrito/${getSesionId()}/items/${producto_id}`, {
      method: 'PUT',
      body: JSON.stringify({ cantidad }),
    }),
  eliminar: (producto_id: string) =>
    request<Carrito>(`/carrito/${getSesionId()}/items/${producto_id}`, { method: 'DELETE' }),
  limpiar: () =>
    request<void>(`/carrito/${getSesionId()}`, { method: 'DELETE' }),
};

// -- Ventas --
export const ventasApi = {
  listar: (params?: { cliente_id?: string; limite?: number }) => {
    const q = new URLSearchParams();
    if (params?.cliente_id) q.set('cliente_id', params.cliente_id);
    if (params?.limite) q.set('limite', String(params.limite));
    const qs = q.toString();
    return request<Venta[]>(`/ventas${qs ? `?${qs}` : ''}`);
  },
  obtener: (id: string) => request<Venta>(`/ventas/${id}`),
  crear: () =>
    request<Venta>('/ventas', {
      method: 'POST',
      body: JSON.stringify({ sesion_id: getSesionId() }),
    }),
  cancelar: (id: string) =>
    request<Venta>(`/ventas/${id}/cancelar`, { method: 'POST' }),
  stats: () => request<DashboardStats>('/ventas/stats'),
};
