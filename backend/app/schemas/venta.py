from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VentaItem(BaseModel):
    producto_id: str
    producto_nombre: str
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)
    subtotal: float = Field(..., ge=0)


class VentaCreate(BaseModel):
    sesion_id: str
    cliente_id: Optional[str] = None


class VentaInDB(BaseModel):
    id: str = Field(alias="_id")
    folio: str
    cliente_id: Optional[str] = None
    items: List[VentaItem]
    total: float
    fecha: datetime = Field(default_factory=datetime.utcnow)
    estado: str = "completada"  # completada | cancelada

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class VentaResponse(BaseModel):
    id: str
    folio: str
    cliente_id: Optional[str] = None
    items: List[VentaItem]
    total: float
    fecha: str
    estado: str

    class Config:
        populate_by_name = True


class DashboardStats(BaseModel):
    ventas_hoy: int = 0
    total_ventas_hoy: float = 0
    total_clientes: int = 0
    total_productos: int = 0
    productos_bajo_stock: int = 0
    ventas_totales: float = 0
    top_productos: List[dict] = []
