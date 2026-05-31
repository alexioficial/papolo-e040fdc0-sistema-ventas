from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse


async def listar_clientes(
    db: AsyncIOMotorDatabase,
    busqueda: Optional[str] = None,
) -> List[ClienteResponse]:
    """Lista clientes con búsqueda opcional."""
    filtro = {}
    if busqueda:
        filtro["$or"] = [
            {"nombre": {"$regex": busqueda, "$options": "i"}},
            {"email": {"$regex": busqueda, "$options": "i"}},
            {"telefono": {"$regex": busqueda, "$options": "i"}},
        ]

    cursor = db.clientes.find(filtro).sort("nombre", 1)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = doc.get("created_at", "").isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", ""))
        doc["updated_at"] = doc.get("updated_at", "").isoformat() if hasattr(doc.get("updated_at"), "isoformat") else str(doc.get("updated_at", ""))
        resultados.append(ClienteResponse(**doc))
    return resultados


async def obtener_cliente(db: AsyncIOMotorDatabase, cliente_id: str) -> Optional[ClienteResponse]:
    """Obtiene un cliente por ID."""
    try:
        obj_id = ObjectId(cliente_id)
    except:
        return None
    doc = await db.clientes.find_one({"_id": obj_id})
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["created_at"] = doc.get("created_at", "").isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", ""))
    doc["updated_at"] = doc.get("updated_at", "").isoformat() if hasattr(doc.get("updated_at"), "isoformat") else str(doc.get("updated_at", ""))
    return ClienteResponse(**doc)


async def crear_cliente(db: AsyncIOMotorDatabase, cliente: ClienteCreate) -> ClienteResponse:
    """Crea un nuevo cliente."""
    # Verificar email único
    existente = await db.clientes.find_one({"email": cliente.email})
    if existente:
        raise ValueError(f"Ya existe un cliente con el email {cliente.email}")

    doc = cliente.model_dump()
    from datetime import datetime
    now = datetime.utcnow()
    doc["created_at"] = now
    doc["updated_at"] = now
    result = await db.clientes.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["created_at"] = now.isoformat()
    doc["updated_at"] = now.isoformat()
    return ClienteResponse(**doc)


async def actualizar_cliente(
    db: AsyncIOMotorDatabase, cliente_id: str, cliente: ClienteUpdate
) -> Optional[ClienteResponse]:
    """Actualiza un cliente existente."""
    try:
        obj_id = ObjectId(cliente_id)
    except:
        return None

    update_data = {k: v for k, v in cliente.model_dump().items() if v is not None}
    if not update_data:
        return await obtener_cliente(db, cliente_id)

    # Verificar email único si se está actualizando
    if "email" in update_data:
        existente = await db.clientes.find_one(
            {"email": update_data["email"], "_id": {"$ne": obj_id}}
        )
        if existente:
            raise ValueError(f"Ya existe otro cliente con el email {update_data['email']}")

    from datetime import datetime
    update_data["updated_at"] = datetime.utcnow()

    result = await db.clientes.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        return None
    return await obtener_cliente(db, cliente_id)


async def eliminar_cliente(db: AsyncIOMotorDatabase, cliente_id: str) -> bool:
    """Elimina un cliente físicamente."""
    try:
        obj_id = ObjectId(cliente_id)
    except:
        return False

    result = await db.clientes.delete_one({"_id": obj_id})
    return result.deleted_count > 0
