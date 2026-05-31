from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str = Field(default="", max_length=2000)
    precio: float = Field(..., gt=0)
    sku: str = Field(..., min_length=1, max_length=50)
    stock: int = Field(default=0, ge=0)
    categoria: str = Field(default="General", max_length=100)
    imagen_url: Optional[str] = None
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=2000)
    precio: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, max_length=100)
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None


class ProductoInDB(ProductoBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProductoResponse(ProductoBase):
    id: str = Field(alias="_id")
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True


class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0)
