from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.venta import VentaCreate, VentaResponse, DashboardStats
from app.schemas.carrito import CarritoItem


async def _generar_folio(db: AsyncIOMotorDatabase) -> str:
    """Genera un folio auto-incremental V-XXXX."""
    ultima_venta = await db.ventas.find_one(
        {}, sort=[("folio", -1)], projection={"folio": 1}
    )
    if ultima_venta and "folio" in ultima_venta:
        num = int(ultima_venta["folio"].split("-")[1]) + 1
    else:
        num = 1
    return f"V-{num:04d}"


async def crear_venta(
    db: AsyncIOMotorDatabase, venta_data: VentaCreate
) -> VentaResponse:
    """
    Crea una venta a partir del carrito.
    - Obtiene items del carrito
    - Descuenta stock atómicamente
    - Genera folio
    - Limpia el carrito
    """
    sesion_id = venta_data.sesion_id

    # 1. Obtener carrito
    carrito = await db.carritos.find_one({"sesion_id": sesion_id})
    if not carrito or not carrito.get("items"):
        raise ValueError("Carrito vacío o no encontrado")

    items_data = carrito["items"]

    # 2. Descontar stock atómicamente (producto por producto)
    for item in items_data:
        try:
            prod_id = ObjectId(item["producto_id"])
        except:
            raise ValueError(f"ID de producto inválido: {item['producto_id']}")

        result = await db.productos.update_one(
            {"_id": prod_id, "stock": {"$gte": item["cantidad"]}},
            {"$inc": {"stock": -item["cantidad"]}}
        )
        if result.modified_count == 0:
            # Revertir descuentos previos — lanzar excepción
            raise ValueError(
                f"Stock insuficiente para: {item.get('producto_nombre', 'producto desconocido')}. "
                "La venta ha sido cancelada."
            )

    # 3. Calcular subtotales y total
    items_venta = []
    total = 0
    for item in items_data:
        subtotal = item["cantidad"] * item["precio_unitario"]
        items_venta.append({
            "producto_id": item["producto_id"],
            "producto_nombre": item["producto_nombre"],
            "cantidad": item["cantidad"],
            "precio_unitario": item["precio_unitario"],
            "subtotal": subtotal,
        })
        total += subtotal

    # 4. Generar folio y crear venta
    folio = await _generar_folio(db)
    from datetime import datetime
    now = datetime.utcnow()

    venta_doc = {
        "folio": folio,
        "cliente_id": venta_data.cliente_id,
        "items": items_venta,
        "total": total,
        "fecha": now,
        "estado": "completada",
    }

    result = await db.ventas.insert_one(venta_doc)

    # 5. Limpiar carrito
    await db.carritos.delete_one({"sesion_id": sesion_id})

    # 6. Devolver respuesta
    venta_doc["_id"] = str(result.inserted_id)
    venta_doc["fecha"] = now.isoformat()
    return VentaResponse(**venta_doc)


async def listar_ventas(
    db: AsyncIOMotorDatabase,
    cliente_id: Optional[str] = None,
    limite: int = 50,
) -> List[VentaResponse]:
    """Lista ventas, opcionalmente filtradas por cliente."""
    filtro = {}
    if cliente_id:
        filtro["cliente_id"] = cliente_id

    cursor = db.ventas.find(filtro).sort("fecha", -1).limit(limite)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["fecha"] = doc["fecha"].isoformat() if hasattr(doc["fecha"], "isoformat") else str(doc["fecha"])
        resultados.append(VentaResponse(**doc))
    return resultados


async def obtener_venta(db: AsyncIOMotorDatabase, venta_id: str) -> Optional[VentaResponse]:
    """Obtiene una venta por ID."""
    try:
        obj_id = ObjectId(venta_id)
    except:
        return None
    doc = await db.ventas.find_one({"_id": obj_id})
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["fecha"] = doc["fecha"].isoformat() if hasattr(doc["fecha"], "isoformat") else str(doc["fecha"])
    return VentaResponse(**doc)


async def cancelar_venta(db: AsyncIOMotorDatabase, venta_id: str) -> Optional[VentaResponse]:
    """Cancela una venta y restaura el stock."""
    try:
        obj_id = ObjectId(venta_id)
    except:
        return None

    venta = await db.ventas.find_one({"_id": obj_id})
    if not venta:
        return None
    if venta["estado"] == "cancelada":
        raise ValueError("La venta ya está cancelada")

    # Restaurar stock
    for item in venta["items"]:
        try:
            prod_id = ObjectId(item["producto_id"])
        except:
            continue
        await db.productos.update_one(
            {"_id": prod_id},
            {"$inc": {"stock": item["cantidad"]}}
        )

    from datetime import datetime
    await db.ventas.update_one(
        {"_id": obj_id},
        {"$set": {"estado": "cancelada"}}
    )

    venta["estado"] = "cancelada"
    venta["_id"] = str(venta["_id"])
    venta["fecha"] = venta["fecha"].isoformat() if hasattr(venta["fecha"], "isoformat") else str(venta["fecha"])
    return VentaResponse(**venta)


async def obtener_stats(db: AsyncIOMotorDatabase) -> DashboardStats:
    """Obtiene estadísticas para el dashboard."""
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)

    # Ventas de hoy
    ventas_hoy_cursor = db.ventas.find({
        "fecha": {"$gte": today_start, "$lt": today_end},
        "estado": "completada",
    })
    ventas_hoy = await ventas_hoy_cursor.to_list(length=1000)
    total_ventas_hoy = sum(v["total"] for v in ventas_hoy)

    # Total clientes
    total_clientes = await db.clientes.count_documents({})

    # Total productos activos
    total_productos = await db.productos.count_documents({"activo": True})

    # Productos con stock bajo (< 5)
    productos_bajo_stock = await db.productos.count_documents(
        {"activo": True, "stock": {"$lt": 5}}
    )

    # Ventas totales (completadas)
    pipeline_ventas_totales = [
        {"$match": {"estado": "completada"}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    result = await db.ventas.aggregate(pipeline_ventas_totales).to_list(length=1)
    ventas_totales = result[0]["total"] if result else 0

    # Top productos más vendidos
    pipeline_top = [
        {"$match": {"estado": "completada"}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.producto_nombre",
            "cantidad_total": {"$sum": "$items.cantidad"},
            "total_vendido": {"$sum": "$items.subtotal"},
        }},
        {"$sort": {"cantidad_total": -1}},
        {"$limit": 5},
    ]
    top_productos = await db.ventas.aggregate(pipeline_top).to_list(length=5)
    top_productos_clean = [
        {"nombre": p["_id"], "cantidad": p["cantidad_total"], "total": p["total_vendido"]}
        for p in top_productos
    ]

    return DashboardStats(
        ventas_hoy=len(ventas_hoy),
        total_ventas_hoy=total_ventas_hoy,
        total_clientes=total_clientes,
        total_productos=total_productos,
        productos_bajo_stock=productos_bajo_stock,
        ventas_totales=ventas_totales,
        top_productos=top_productos_clean,
    )
