from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
import json

# Clase para representar precios en dólares
class PrecioDolar:
    def __init__(self, monto: float):
        self.monto = monto
    
    def __str__(self):
        return f"${self.monto:.2f} USD"
    
    def __repr__(self):
        return f"${self.monto:.2f} USD"
    
    def __float__(self):
        return float(self.monto)
        
# Función para formatear los precios en dólares
def format_precio_usd(precio: float) -> str:
    """Formatea un precio en formato de dólares americanos."""
    if precio is None:
        return None
    return f"${precio:.2f} USD"

# Esquemas para Productos
class ProductoBase(BaseModel):
    nombre: str
    precio: float = Field(..., description="Precio en dólares americanos (USD)")
    stock: int = 0
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None

class Producto(ProductoBase):
    id: int
    fecha_creacion: datetime
    precio_formateado: Optional[str] = None

    class Config:
        orm_mode = True
    
    @validator('precio_formateado', pre=True, always=True)
    def format_precio(cls, v, values):
        """Genera una representación formateada del precio en dólares."""
        precio = values.get('precio')
        if precio is not None:
            return format_precio_usd(precio)
        return None

# Esquemas para Clientes
class ClienteBase(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True

class ClienteCreate(ClienteBase):
    contraseña: str

class Cliente(ClienteBase):
    id: int
    fecha_registro: datetime

    class Config:
        orm_mode = True

# Esquemas para Pedidos
class PedidoBase(BaseModel):
    cliente_id: int
    producto_id: int
    cantidad: int = 1
    precio_unitario: float = Field(..., description="Precio unitario en dólares americanos (USD)")
    total: float = Field(..., description="Total en dólares americanos (USD)")
    notas: Optional[str] = None

class PedidoCreate(PedidoBase):
    pass

class PedidoEstadoUpdate(BaseModel):
    estado: str

class Pedido(PedidoBase):
    id: int
    estado: str
    fecha: datetime
    
    # Campos formateados
    precio_unitario_formateado: Optional[str] = None
    total_formateado: Optional[str] = None
    
    # Información adicional
    cliente: Optional[Cliente] = None
    producto: Optional[Producto] = None

    class Config:
        orm_mode = True
    
    @validator('precio_unitario_formateado', pre=True, always=True)
    def format_precio_unitario(cls, v, values):
        """Genera una representación formateada del precio unitario en dólares."""
        precio = values.get('precio_unitario')
        if precio is not None:
            return format_precio_usd(precio)
        return None
    
    @validator('total_formateado', pre=True, always=True)
    def format_total(cls, v, values):
        """Genera una representación formateada del total en dólares."""
        total = values.get('total')
        if total is not None:
            return format_precio_usd(total)
        return None

# Esquema para autenticación
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int

class TokenData(BaseModel):
    username: str
    user_type: str
    user_id: int
