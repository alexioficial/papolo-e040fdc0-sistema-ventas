from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas.venta import VentaCreate, VentaResponse, DashboardStats
from app.services import ventas as ventas_service

router = APIRouter(prefix="/api/ventas", tags=["ventas"])


@router.get("", response_model=list[VentaResponse])
async def listar_ventas(
    cliente_id: Optional[str] = Query(None),
    limite: int = Query(50, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Lista todas las ventas."""
    return await ventas_service.listar_ventas(db, cliente_id, limite)


@router.get("/stats", response_model=DashboardStats)
async def obtener_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene estadísticas del dashboard."""
    return await ventas_service.obtener_stats(db)


@router.get("/{venta_id}", response_model=VentaResponse)
async def obtener_venta(
    venta_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene una venta por ID."""
    venta = await ventas_service.obtener_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("", response_model=VentaResponse, status_code=201)
async def crear_venta(
    venta_data: VentaCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Crea una nueva venta (checkout del carrito)."""
    try:
        return await ventas_service.crear_venta(db, venta_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/cancelar", response_model=VentaResponse)
async def cancelar_venta(
    venta_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Cancela una venta y restaura el stock."""
    try:
        result = await ventas_service.cancelar_venta(db, venta_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return result
