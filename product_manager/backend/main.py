"""
main.py - Servidor FastAPI: endpoints CRUD y estadísticas
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

try:
    from database import engine, get_db, Base
    from models import (
        ProductoDB, ProductoCreate, ProductoUpdate, ProductoResponse,
        DashboardStats, CategoriaStats, BajoStockResponse
    )
    import crud
except ImportError:
    from .database import engine, get_db, Base
    from .models import (
        ProductoDB, ProductoCreate, ProductoUpdate, ProductoResponse,
        DashboardStats, CategoriaStats, BajoStockResponse
    )
    from . import crud

# Crear tablas si no existen (útil para desarrollo)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gestión de Productos",
    description="Sistema de inventario para PyMEs - Backend FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir conexiones desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En producción, limitar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/", tags=["Sistema"])
def root():
    return {"status": "ok", "message": "API Gestión de Productos activa", "version": "1.0.0"}


@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Base de datos no disponible: {str(e)}")


# ============================================================
# PRODUCTOS - CRUD
# ============================================================

@app.get("/productos", response_model=List[ProductoResponse], tags=["Productos"])
def listar_productos(
    skip:      int           = Query(0, ge=0, description="Registros a omitir"),
    limit:     int           = Query(1000, ge=1, le=5000, description="Máximo de registros"),
    search:    Optional[str] = Query(None, description="Buscar en nombre, SKU, descripción o proveedor"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    bajo_stock: bool         = Query(False, description="Solo productos bajo stock mínimo"),
    db: Session = Depends(get_db)
):
    """Obtener todos los productos con filtros opcionales."""
    return crud.get_productos(db, skip=skip, limit=limit, search=search, categoria=categoria, bajo_stock=bajo_stock)


@app.get("/productos/count", tags=["Productos"])
def contar_productos(
    search:    Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Contar productos totales con filtros."""
    total = crud.count_productos(db, search=search, categoria=categoria)
    return {"total": total}


@app.get("/productos/categorias", response_model=List[str], tags=["Productos"])
def listar_categorias(db: Session = Depends(get_db)):
    """Obtener lista de categorías únicas."""
    return crud.get_categorias(db)


@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto específico por ID."""
    producto = crud.get_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail=f"Producto {producto_id} no encontrado")
    return producto


@app.post("/productos", response_model=ProductoResponse, status_code=201, tags=["Productos"])
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto."""
    return crud.create_producto(db, producto)


@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
def actualizar_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
    """Actualizar un producto existente."""
    return crud.update_producto(db, producto_id, producto)


@app.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Eliminar un producto por ID."""
    crud.delete_producto(db, producto_id)
    return {"message": f"Producto {producto_id} eliminado correctamente"}


# ============================================================
# ESTADÍSTICAS Y DASHBOARD
# ============================================================

@app.get("/stats/dashboard", response_model=DashboardStats, tags=["Estadísticas"])
def dashboard_stats(db: Session = Depends(get_db)):
    """KPIs principales para el panel de control."""
    return crud.get_dashboard_stats(db)


@app.get("/stats/categorias", response_model=List[CategoriaStats], tags=["Estadísticas"])
def stats_por_categoria(db: Session = Depends(get_db)):
    """Estadísticas agrupadas por categoría."""
    return crud.get_stats_por_categoria(db)


@app.get("/stats/bajo-stock", response_model=List[BajoStockResponse], tags=["Estadísticas"])
def productos_bajo_stock(db: Session = Depends(get_db)):
    """Productos que necesitan reabastecimiento."""
    return crud.get_productos_bajo_stock(db)


# ============================================================
# ENTRADA PRINCIPAL
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
