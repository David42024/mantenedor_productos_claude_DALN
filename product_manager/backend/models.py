"""
models.py - Modelos SQLAlchemy (ORM) y esquemas Pydantic para validación
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import validates
from pydantic import BaseModel, Field, validator
from database import Base


# ============================================================
# MODELO ORM - SQLAlchemy (representa la tabla en PostgreSQL)
# ============================================================

class ProductoDB(Base):
    """Modelo SQLAlchemy para la tabla 'productos'."""
    __tablename__ = "productos"

    id                         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku                        = Column(String(50), unique=True, nullable=False, index=True)
    nombre                     = Column(String(200), nullable=False)
    descripcion                = Column(Text, nullable=True)
    categoria                  = Column(String(100), nullable=False, index=True)
    precio_compra              = Column(Numeric(12, 2), nullable=False)
    precio_venta               = Column(Numeric(12, 2), nullable=False)
    stock_actual               = Column(Integer, nullable=False, default=0)
    stock_minimo               = Column(Integer, nullable=False, default=0)
    proveedor                  = Column(String(200), nullable=True)
    fecha_creacion             = Column(DateTime(timezone=True), server_default=func.now())
    fecha_ultima_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @validates("precio_compra", "precio_venta")
    def validate_precios(self, key, value):
        if value is not None and float(value) < 0:
            raise ValueError(f"{key} no puede ser negativo")
        return value

    @validates("stock_actual", "stock_minimo")
    def validate_stock(self, key, value):
        if value is not None and int(value) < 0:
            raise ValueError(f"{key} no puede ser negativo")
        return value


# ============================================================
# ESQUEMAS PYDANTIC - Validación y serialización API
# ============================================================

class ProductoBase(BaseModel):
    """Campos comunes a todos los esquemas de producto."""
    sku:          str   = Field(..., min_length=1, max_length=50,  description="Código SKU único del producto")
    nombre:       str   = Field(..., min_length=1, max_length=200, description="Nombre del producto")
    descripcion:  Optional[str] = Field(None, description="Descripción detallada")
    categoria:    str   = Field(..., min_length=1, max_length=100, description="Categoría del producto")
    precio_compra: float = Field(..., ge=0, description="Precio de compra/costo")
    precio_venta:  float = Field(..., ge=0, description="Precio de venta al público")
    stock_actual:  int   = Field(..., ge=0, description="Cantidad actual en inventario")
    stock_minimo:  int   = Field(0, ge=0,  description="Nivel mínimo de stock para reorden")
    proveedor:    Optional[str] = Field(None, max_length=200, description="Nombre del proveedor")

    @validator("precio_venta")
    def precio_venta_mayor_compra(cls, v, values):
        if "precio_compra" in values and v < values["precio_compra"]:
            raise ValueError("El precio de venta no puede ser menor al precio de compra")
        return v

    @validator("sku")
    def sku_uppercase(cls, v):
        return v.strip().upper()

    @validator("nombre", "categoria")
    def strip_strings(cls, v):
        return v.strip() if v else v

    class Config:
        from_attributes = True


class ProductoCreate(ProductoBase):
    """Esquema para crear un nuevo producto (POST)."""
    pass


class ProductoUpdate(BaseModel):
    """Esquema para actualizar un producto (PUT) - todos los campos opcionales."""
    sku:          Optional[str]   = Field(None, min_length=1, max_length=50)
    nombre:       Optional[str]   = Field(None, min_length=1, max_length=200)
    descripcion:  Optional[str]   = None
    categoria:    Optional[str]   = Field(None, min_length=1, max_length=100)
    precio_compra: Optional[float] = Field(None, ge=0)
    precio_venta:  Optional[float] = Field(None, ge=0)
    stock_actual:  Optional[int]   = Field(None, ge=0)
    stock_minimo:  Optional[int]   = Field(None, ge=0)
    proveedor:    Optional[str]   = Field(None, max_length=200)

    @validator("sku", pre=True, always=False)
    def sku_uppercase_update(cls, v):
        return v.strip().upper() if v else v

    class Config:
        from_attributes = True


class ProductoResponse(ProductoBase):
    """Esquema de respuesta que incluye campos generados por el servidor."""
    id:                         int
    fecha_creacion:             Optional[datetime]
    fecha_ultima_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================
# ESQUEMAS DE ESTADÍSTICAS / DASHBOARD
# ============================================================

class DashboardStats(BaseModel):
    """KPIs principales para el panel de control."""
    total_productos:         int
    valor_total_inventario:  float
    productos_bajo_stock:    int
    producto_mas_valioso:    Optional[str]
    valor_producto_top:      Optional[float]
    total_categorias:        int
    margen_promedio_pct:     float

    class Config:
        from_attributes = True


class CategoriaStats(BaseModel):
    """Estadísticas agrupadas por categoría."""
    categoria:        str
    total_productos:  int
    valor_inventario: float
    stock_total:      int

    class Config:
        from_attributes = True


class BajoStockResponse(BaseModel):
    """Producto con bajo nivel de stock para reorden."""
    id:            int
    sku:           str
    nombre:        str
    categoria:     str
    stock_actual:  int
    stock_minimo:  int
    deficit:       int
    proveedor:     Optional[str]

    class Config:
        from_attributes = True
