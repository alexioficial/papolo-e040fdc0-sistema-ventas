export interface Producto {
  _id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  sku: string;
  stock: number;
  categoria: string;
  imagen_url: string | null;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductoCreate {
  nombre: string;
  descripcion?: string;
  precio: number;
  sku: string;
  stock?: number;
  categoria?: string;
  imagen_url?: string | null;
}

export interface ProductoUpdate {
  nombre?: string;
  descripcion?: string;
  precio?: number;
  sku?: string;
  stock?: number;
  categoria?: string;
  imagen_url?: string | null;
  activo?: boolean;
}

export interface Cliente {
  _id: string;
  nombre: string;
  email: string;
  telefono: string | null;
  direccion: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClienteCreate {
  nombre: string;
  email: string;
  telefono?: string;
  direccion?: string;
}

export interface Venta {
  _id: string;
  folio: string;
  cliente_id: string | null;
  items: VentaItem[];
  total: number;
  fecha: string;
  estado: string;
}

export interface VentaItem {
  producto_id: string;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface CarritoItem {
  producto_id: string;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
}

export interface Carrito {
  id: string;
  sesion_id: string;
  items: CarritoItem[];
  total: number;
}

export interface DashboardStats {
  ventas_hoy: number;
  total_ventas_hoy: number;
  total_clientes: number;
  total_productos: number;
  productos_bajo_stock: number;
  ventas_totales: number;
  top_productos: { nombre: string; cantidad: number; total: number }[];
}
