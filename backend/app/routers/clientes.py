from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.services import clientes as clientes_service

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
async def listar_clientes(
    busqueda: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Lista todos los clientes."""
    return await clientes_service.listar_clientes(db, busqueda)


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(
    cliente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene un cliente por ID."""
    cliente = await clientes_service.obtener_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("", response_model=ClienteResponse, status_code=201)
async def crear_cliente(
    cliente: ClienteCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Crea un nuevo cliente."""
    try:
        return await clientes_service.crear_cliente(db, cliente)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: str,
    cliente: ClienteUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Actualiza un cliente existente."""
    try:
        result = await clientes_service.actualizar_cliente(db, cliente_id, cliente)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result


@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina un cliente."""
    result = await clientes_service.eliminar_cliente(db, cliente_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")


@router.get("/{cliente_id}/ventas", response_model=list)
async def ventas_cliente(
    cliente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Obtiene el historial de ventas de un cliente."""
    from app.services.ventas import listar_ventas
    return await listar_ventas(db, cliente_id=cliente_id)
