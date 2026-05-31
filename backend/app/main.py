from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import connect_db, close_db
from app.routers import productos, clientes, carrito, ventas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    print("🚀 Iniciando Sistema de Ventas...")
    await connect_db()
    print(f"🌐 Servidor listo en puerto 8000")
    yield
    await close_db()
    print("👋 Servidor detenido")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(carrito.router)
app.include_router(ventas.router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    from app.database import client
    mongo_status = "connected" if client is not None else "disconnected"
    return {"status": "ok", "app": settings.app_name, "mongo": mongo_status}


# Servir frontend estático (si existe)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"📁 Sirviendo frontend estático desde {static_dir}")
