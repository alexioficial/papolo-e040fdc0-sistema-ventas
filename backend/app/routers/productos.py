from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse, StockUpdate
from app.services import productos as productos_service

router = APIRouter(prefix="/api/productos", tags=["productos"])


@router.get("", response_model=list[ProductoResponse])
async def listar_productos(
    categoria: Optional[str] = Query(None),
    busqueda: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Lista todos los productos activos."""
    return await productos_service.listar_productos(db, categoria, busqueda)


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(
    producto_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene un producto por ID."""
    producto = await productos_service.obtener_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("", response_model=ProductoResponse, status_code=201)
async def crear_producto(
    producto: ProductoCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Crea un nuevo producto."""
    # Verificar SKU único
    from bson import ObjectId
    existente = await db.productos.find_one({"sku": producto.sku})
    if existente:
        raise HTTPException(status_code=400, detail=f"Ya existe un producto con SKU {producto.sku}")
    return await productos_service.crear_producto(db, producto)


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: str,
    producto: ProductoUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Actualiza un producto existente."""
    try:
        result = await productos_service.actualizar_producto(db, producto_id, producto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(
    producto_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina un producto (desactivación lógica)."""
    result = await productos_service.eliminar_producto(db, producto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.patch("/{producto_id}/stock", response_model=ProductoResponse)
async def ajustar_stock(
    producto_id: str,
    stock_data: StockUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Ajusta el stock de un producto."""
    result = await productos_service.ajustar_stock(db, producto_id, stock_data.stock)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result
