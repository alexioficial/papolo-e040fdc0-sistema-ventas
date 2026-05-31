from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

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


# Servir frontend estático
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    # Servir assets estáticos de _app
    app.mount("/_app", StaticFiles(directory=str(static_dir / "_app")), name="assets")

    # Servir favicon
    favicon_path = static_dir / "favicon.png"
    if favicon_path.exists():
        @app.get("/favicon.png")
        async def favicon():
            return FileResponse(favicon_path)

    # Servir archivos estáticos y rutas SPA
    @app.api_route("/{path:path}", methods=["GET"])
    async def spa(request: Request, path: str):
        # No interferir con rutas de API
        if path.startswith("api/") or path.startswith("api"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Intentar servir archivo estático exacto
        file_path = static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Intentar servir archivo HTML por nombre
        html_path = static_dir / f"{path}.html"
        if html_path.exists():
            return FileResponse(html_path)

        # Intentar index.html dentro de directorio
        dir_index = static_dir / path / "index.html"
        if dir_index.exists():
            return FileResponse(dir_index)

        # Fallback SPA: servir index.html
        index_html = static_dir / "index.html"
        if index_html.exists():
            return FileResponse(index_html)

        return JSONResponse({"detail": "Not Found"}, status_code=404)
