from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoInDB, ProductoResponse


async def listar_productos(
    db: AsyncIOMotorDatabase,
    categoria: Optional[str] = None,
    busqueda: Optional[str] = None,
    solo_activos: bool = True,
) -> List[ProductoResponse]:
    """Lista productos con filtros opcionales."""
    filtro = {}
    if solo_activos:
        filtro["activo"] = True
    if categoria:
        filtro["categoria"] = categoria
    if busqueda:
        filtro["$or"] = [
            {"nombre": {"$regex": busqueda, "$options": "i"}},
            {"sku": {"$regex": busqueda, "$options": "i"}},
            {"descripcion": {"$regex": busqueda, "$options": "i"}},
        ]

    cursor = db.productos.find(filtro).sort("nombre", 1)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = doc.get("created_at", "").isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", ""))
        doc["updated_at"] = doc.get("updated_at", "").isoformat() if hasattr(doc.get("updated_at"), "isoformat") else str(doc.get("updated_at", ""))
        resultados.append(ProductoResponse(**doc))
    return resultados


async def obtener_producto(db: AsyncIOMotorDatabase, producto_id: str) -> Optional[ProductoResponse]:
    """Obtiene un producto por ID."""
    try:
        obj_id = ObjectId(producto_id)
    except:
        return None
    doc = await db.productos.find_one({"_id": obj_id})
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["created_at"] = doc.get("created_at", "").isoformat() if hasattr(doc.get("created_at"), "isoformat") else str(doc.get("created_at", ""))
    doc["updated_at"] = doc.get("updated_at", "").isoformat() if hasattr(doc.get("updated_at"), "isoformat") else str(doc.get("updated_at", ""))
    return ProductoResponse(**doc)


async def crear_producto(db: AsyncIOMotorDatabase, producto: ProductoCreate) -> ProductoResponse:
    """Crea un nuevo producto."""
    doc = producto.model_dump()
    from datetime import datetime
    now = datetime.utcnow()
    doc["created_at"] = now
    doc["updated_at"] = now
    result = await db.productos.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["created_at"] = now.isoformat()
    doc["updated_at"] = now.isoformat()
    return ProductoResponse(**doc)


async def actualizar_producto(
    db: AsyncIOMotorDatabase, producto_id: str, producto: ProductoUpdate
) -> Optional[ProductoResponse]:
    """Actualiza un producto existente."""
    try:
        obj_id = ObjectId(producto_id)
    except:
        return None

    update_data = {k: v for k, v in producto.model_dump().items() if v is not None}
    if not update_data:
        return await obtener_producto(db, producto_id)

    from datetime import datetime
    update_data["updated_at"] = datetime.utcnow()

    result = await db.productos.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        return None
    return await obtener_producto(db, producto_id)


async def eliminar_producto(db: AsyncIOMotorDatabase, producto_id: str) -> bool:
    """Eliminación lógica: desactiva el producto."""
    try:
        obj_id = ObjectId(producto_id)
    except:
        return False

    from datetime import datetime
    result = await db.productos.update_one(
        {"_id": obj_id},
        {"$set": {"activo": False, "updated_at": datetime.utcnow()}}
    )
    return result.matched_count > 0


async def ajustar_stock(db: AsyncIOMotorDatabase, producto_id: str, nuevo_stock: int) -> Optional[ProductoResponse]:
    """Ajusta el stock de un producto."""
    try:
        obj_id = ObjectId(producto_id)
    except:
        return None

    from datetime import datetime
    result = await db.productos.update_one(
        {"_id": obj_id},
        {"$set": {"stock": nuevo_stock, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        return None
    return await obtener_producto(db, producto_id)
