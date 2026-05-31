# Sistema de Ventas

Sistema completo de ventas con backend FastAPI + MongoDB y frontend SvelteKit.

## 🚀 Stack

- **Backend**: FastAPI (Python 3.12) + MongoDB (Motor async)
- **Frontend**: SvelteKit 5 + TypeScript (compilado a estático)
- **Base de datos**: MongoDB

## 📋 Funcionalidades

- **Productos**: CRUD completo con categorías, stock, búsqueda
- **Clientes**: Gestión de clientes con historial de compras
- **Carrito**: Carrito de compras por sesión con persistencia
- **Ventas**: Checkout atómico con descuento de stock, cancelación con restauración
- **Dashboard**: Estadísticas de ventas, top productos, stock bajo

## 🛠️ Desarrollo local

### Requisitos
- Python 3.12+
- Node.js 20+
- MongoDB (local o Atlas)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Build producción
```bash
cd backend
bash build.sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔌 API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET/POST | `/api/productos` | Listar/Crear productos |
| GET/PUT/DELETE | `/api/productos/{id}` | CRUD producto |
| PATCH | `/api/productos/{id}/stock` | Ajustar stock |
| GET/POST | `/api/clientes` | Listar/Crear clientes |
| GET/PUT/DELETE | `/api/clientes/{id}` | CRUD cliente |
| GET | `/api/carrito/{sesion_id}` | Obtener carrito |
| POST | `/api/carrito/{sesion_id}/items` | Agregar item |
| PUT/DELETE | `/api/carrito/{sesion_id}/items/{id}` | Actualizar/Eliminar item |
| POST | `/api/ventas` | Checkout (crear venta) |
| GET | `/api/ventas` | Listar ventas |
| GET | `/api/ventas/stats` | Dashboard stats |
| POST | `/api/ventas/{id}/cancelar` | Cancelar venta |

## 🐳 Docker

```bash
docker build -t sistema-ventas .
docker run -p 8000:8000 -e MONGODB_URI=mongodb://host.docker.internal:27017/sistema_ventas sistema-ventas
```
