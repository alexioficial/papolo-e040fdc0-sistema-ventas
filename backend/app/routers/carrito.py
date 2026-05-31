from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas.carrito import CarritoItemCreate, CarritoItemUpdate, CarritoResponse
from app.services import carrito as carrito_service

router = APIRouter(prefix="/api/carrito", tags=["carrito"])


@router.get("/{sesion_id}", response_model=CarritoResponse)
async def obtener_carrito(
    sesion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene el carrito de una sesión."""
    carrito = await carrito_service.obtener_carrito(db, sesion_id)
    if not carrito:
        # Devolver carrito vacío
        return CarritoResponse(id="", sesion_id=sesion_id, items=[], total=0)
    return carrito


@router.post("/{sesion_id}/items", response_model=CarritoResponse, status_code=201)
async def agregar_item(
    sesion_id: str,
    item: CarritoItemCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Agrega un producto al carrito."""
    try:
        return await carrito_service.agregar_item(db, sesion_id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{sesion_id}/items/{producto_id}", response_model=CarritoResponse)
async def actualizar_item(
    sesion_id: str,
    producto_id: str,
    item: CarritoItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Actualiza la cantidad de un item en el carrito."""
    try:
        return await carrito_service.actualizar_item(db, sesion_id, producto_id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sesion_id}/items/{producto_id}", response_model=CarritoResponse)
async def eliminar_item(
    sesion_id: str,
    producto_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina un item del carrito."""
    try:
        return await carrito_service.eliminar_item(db, sesion_id, producto_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sesion_id}", status_code=204)
async def limpiar_carrito(
    sesion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Limpia todo el carrito."""
    await carrito_service.limpiar_carrito(db, sesion_id)
