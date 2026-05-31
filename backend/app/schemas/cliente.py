from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=500)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=500)


class ClienteInDB(ClienteBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ClienteResponse(ClienteBase):
    id: str = Field(alias="_id")
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
