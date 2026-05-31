from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CarritoItem(BaseModel):
    producto_id: str
    producto_nombre: str
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)


class CarritoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)


class CarritoItemUpdate(BaseModel):
    cantidad: int = Field(..., ge=0)  # 0 = eliminar


class CarritoInDB(BaseModel):
    id: str = Field(alias="_id")
    sesion_id: str
    items: List[CarritoItem] = []
    total: float = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class CarritoResponse(BaseModel):
    id: str
    sesion_id: str
    items: List[CarritoItem]
    total: float

    class Config:
        populate_by_name = True
