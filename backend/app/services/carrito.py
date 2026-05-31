from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.carrito import CarritoItem, CarritoItemCreate, CarritoItemUpdate, CarritoResponse


async def obtener_carrito(db: AsyncIOMotorDatabase, sesion_id: str) -> Optional[CarritoResponse]:
    """Obtiene el carrito de una sesión."""
    doc = await db.carritos.find_one({"sesion_id": sesion_id})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return CarritoResponse(**doc)


async def _recalcular_total(items: List[dict]) -> float:
    """Calcula el total del carrito."""
    return sum(item["cantidad"] * item["precio_unitario"] for item in items)


async def agregar_item(
    db: AsyncIOMotorDatabase, sesion_id: str, item_data: CarritoItemCreate
) -> CarritoResponse:
    """Agrega un producto al carrito. Si ya existe, suma cantidad."""
    # Obtener producto para validar precio y nombre
    try:
        prod_id = ObjectId(item_data.producto_id)
    except:
        raise ValueError("ID de producto inválido")

    producto = await db.productos.find_one({"_id": prod_id, "activo": True})
    if not producto:
        raise ValueError("Producto no encontrado o inactivo")

    if producto["stock"] < item_data.cantidad:
        raise ValueError(f"Stock insuficiente. Disponible: {producto['stock']}")

    from datetime import datetime
    now = datetime.utcnow()

    # Buscar carrito existente o crear uno nuevo
    carrito = await db.carritos.find_one({"sesion_id": sesion_id})
    if not carrito:
        # Crear nuevo carrito
        nuevo_carrito = {
            "sesion_id": sesion_id,
            "items": [],
            "total": 0,
            "updated_at": now,
            "created_at": now,
        }
        result = await db.carritos.insert_one(nuevo_carrito)
        carrito = await db.carritos.find_one({"_id": result.inserted_id})

    # Buscar si el producto ya está en el carrito
    items = list(carrito["items"])
    encontrado = False
    for i, item in enumerate(items):
        if str(item["producto_id"]) == item_data.producto_id:
            nueva_cant = item["cantidad"] + item_data.cantidad
            if nueva_cant > producto["stock"]:
                raise ValueError(f"Stock insuficiente. Disponible: {producto['stock']}")
            items[i]["cantidad"] = nueva_cant
            encontrado = True
            break

    if not encontrado:
        nuevo_item = {
            "producto_id": item_data.producto_id,
            "producto_nombre": producto["nombre"],
            "cantidad": item_data.cantidad,
            "precio_unitario": producto["precio"],
        }
        items.append(nuevo_item)

    total = await _recalcular_total(items)

    await db.carritos.update_one(
        {"sesion_id": sesion_id},
        {"$set": {"items": items, "total": total, "updated_at": now}}
    )

    doc = await db.carritos.find_one({"sesion_id": sesion_id})
    doc["id"] = str(doc["_id"])
    return CarritoResponse(**doc)


async def actualizar_item(
    db: AsyncIOMotorDatabase, sesion_id: str, producto_id: str, item_data: CarritoItemUpdate
) -> CarritoResponse:
    """Actualiza la cantidad de un item (0 = eliminar)."""
    carrito = await db.carritos.find_one({"sesion_id": sesion_id})
    if not carrito:
        raise ValueError("Carrito no encontrado")

    items = list(carrito["items"])
    from datetime import datetime
    now = datetime.utcnow()

    if item_data.cantidad == 0:
        # Eliminar item
        items = [i for i in items if str(i["producto_id"]) != producto_id]
    else:
        for i, item in enumerate(items):
            if str(item["producto_id"]) == producto_id:
                # Validar stock
                try:
                    prod_obj_id = ObjectId(producto_id)
                except:
                    raise ValueError("ID de producto inválido")
                producto = await db.productos.find_one({"_id": prod_obj_id})
                if producto and item_data.cantidad > producto["stock"]:
                    raise ValueError(f"Stock insuficiente. Disponible: {producto['stock']}")
                items[i]["cantidad"] = item_data.cantidad
                break
        else:
            raise ValueError("Producto no encontrado en el carrito")

    total = await _recalcular_total(items)

    await db.carritos.update_one(
        {"sesion_id": sesion_id},
        {"$set": {"items": items, "total": total, "updated_at": now}}
    )

    doc = await db.carritos.find_one({"sesion_id": sesion_id})
    doc["id"] = str(doc["_id"])
    return CarritoResponse(**doc)


async def eliminar_item(
    db: AsyncIOMotorDatabase, sesion_id: str, producto_id: str
) -> CarritoResponse:
    """Elimina un item del carrito."""
    return await actualizar_item(
        db, sesion_id, producto_id, CarritoItemUpdate(cantidad=0)
    )


async def limpiar_carrito(db: AsyncIOMotorDatabase, sesion_id: str) -> bool:
    """Limpia todos los items del carrito."""
    result = await db.carritos.delete_one({"sesion_id": sesion_id})
    return result.deleted_count > 0
