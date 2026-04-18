"""
crud.py - Lógica de operaciones de base de datos (Create, Read, Update, Delete)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case
from models import ProductoDB, ProductoCreate, ProductoUpdate, DashboardStats, CategoriaStats, BajoStockResponse
from fastapi import HTTPException


# ============================================================
# OPERACIONES CRUD
# ============================================================

def get_producto(db: Session, producto_id: int) -> Optional[ProductoDB]:
    """Obtener un producto por ID."""
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()


def get_producto_by_sku(db: Session, sku: str) -> Optional[ProductoDB]:
    """Obtener un producto por SKU."""
    return db.query(ProductoDB).filter(ProductoDB.sku == sku.upper()).first()


def get_productos(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    categoria: Optional[str] = None,
    bajo_stock: bool = False
) -> List[ProductoDB]:
    """
    Obtener lista de productos con filtros opcionales.
    - search: busca en nombre, SKU o descripción
    - categoria: filtra por categoría exacta
    - bajo_stock: solo productos donde stock_actual < stock_minimo
    """
    query = db.query(ProductoDB)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (ProductoDB.nombre.ilike(term)) |
            (ProductoDB.sku.ilike(term)) |
            (ProductoDB.descripcion.ilike(term)) |
            (ProductoDB.proveedor.ilike(term))
        )

    if categoria:
        query = query.filter(ProductoDB.categoria == categoria)

    if bajo_stock:
        query = query.filter(ProductoDB.stock_actual < ProductoDB.stock_minimo)

    return query.order_by(ProductoDB.id).offset(skip).limit(limit).all()


def count_productos(db: Session, search: Optional[str] = None, categoria: Optional[str] = None) -> int:
    """Contar total de productos con filtros."""
    query = db.query(func.count(ProductoDB.id))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (ProductoDB.nombre.ilike(term)) |
            (ProductoDB.sku.ilike(term))
        )
    if categoria:
        query = query.filter(ProductoDB.categoria == categoria)
    return query.scalar()


def create_producto(db: Session, producto: ProductoCreate) -> ProductoDB:
    """Crear un nuevo producto en la base de datos."""
    # Verificar SKU único
    existing = get_producto_by_sku(db, producto.sku)
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe un producto con SKU '{producto.sku}'")

    db_producto = ProductoDB(**producto.dict())
    db.add(db_producto)
    try:
        db.commit()
        db.refresh(db_producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")
    return db_producto


def update_producto(db: Session, producto_id: int, producto: ProductoUpdate) -> ProductoDB:
    """Actualizar un producto existente."""
    db_producto = get_producto(db, producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")

    # Solo actualiza campos enviados (no None)
    update_data = producto.dict(exclude_unset=True)

    # Verificar SKU único si se está cambiando
    if "sku" in update_data:
        existing = get_producto_by_sku(db, update_data["sku"])
        if existing and existing.id != producto_id:
            raise HTTPException(status_code=400, detail=f"Ya existe otro producto con SKU '{update_data['sku']}'")

    for field, value in update_data.items():
        setattr(db_producto, field, value)

    try:
        db.commit()
        db.refresh(db_producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
    return db_producto


def delete_producto(db: Session, producto_id: int) -> bool:
    """Eliminar un producto por ID."""
    db_producto = get_producto(db, producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")
    try:
        db.delete(db_producto)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
    return True


# ============================================================
# ESTADÍSTICAS Y DASHBOARD
# ============================================================

def get_dashboard_stats(db: Session) -> DashboardStats:
    """Calcular KPIs principales para el panel de control."""
    total_productos = db.query(func.count(ProductoDB.id)).scalar() or 0
    total_categorias = db.query(func.count(func.distinct(ProductoDB.categoria))).scalar() or 0

    # Valor total inventario = SUM(stock_actual * precio_compra)
    valor_inventario = db.query(
        func.sum(ProductoDB.stock_actual * ProductoDB.precio_compra)
    ).scalar() or 0.0

    # Productos bajo stock
    bajo_stock = db.query(func.count(ProductoDB.id)).filter(
        ProductoDB.stock_actual < ProductoDB.stock_minimo
    ).scalar() or 0

    # Producto más valioso (stock_actual * precio_compra)
    top_producto = db.query(
        ProductoDB.nombre,
        (ProductoDB.stock_actual * ProductoDB.precio_compra).label("valor")
    ).order_by(
        (ProductoDB.stock_actual * ProductoDB.precio_compra).desc()
    ).first()

    # Margen promedio
    margen_avg = db.query(
        func.avg(
            case(
                (ProductoDB.precio_compra > 0,
                 (ProductoDB.precio_venta - ProductoDB.precio_compra) / ProductoDB.precio_compra * 100),
                else_=0
            )
        )
    ).scalar() or 0.0

    return DashboardStats(
        total_productos=total_productos,
        valor_total_inventario=float(valor_inventario),
        productos_bajo_stock=bajo_stock,
        producto_mas_valioso=top_producto.nombre if top_producto else None,
        valor_producto_top=float(top_producto.valor) if top_producto else None,
        total_categorias=total_categorias,
        margen_promedio_pct=float(margen_avg)
    )


def get_stats_por_categoria(db: Session) -> List[CategoriaStats]:
    """Estadísticas agrupadas por categoría."""
    resultados = db.query(
        ProductoDB.categoria,
        func.count(ProductoDB.id).label("total_productos"),
        func.sum(ProductoDB.stock_actual * ProductoDB.precio_compra).label("valor_inventario"),
        func.sum(ProductoDB.stock_actual).label("stock_total")
    ).group_by(ProductoDB.categoria).order_by(
        func.count(ProductoDB.id).desc()
    ).all()

    return [
        CategoriaStats(
            categoria=r.categoria,
            total_productos=r.total_productos,
            valor_inventario=float(r.valor_inventario or 0),
            stock_total=r.stock_total or 0
        )
        for r in resultados
    ]


def get_productos_bajo_stock(db: Session) -> List[BajoStockResponse]:
    """Listar productos que necesitan reabastecimiento."""
    productos = db.query(ProductoDB).filter(
        ProductoDB.stock_actual < ProductoDB.stock_minimo
    ).order_by(
        (ProductoDB.stock_minimo - ProductoDB.stock_actual).desc()
    ).all()

    return [
        BajoStockResponse(
            id=p.id,
            sku=p.sku,
            nombre=p.nombre,
            categoria=p.categoria,
            stock_actual=p.stock_actual,
            stock_minimo=p.stock_minimo,
            deficit=p.stock_minimo - p.stock_actual,
            proveedor=p.proveedor
        )
        for p in productos
    ]


def get_categorias(db: Session) -> List[str]:
    """Obtener lista de todas las categorías existentes."""
    result = db.query(ProductoDB.categoria).distinct().order_by(ProductoDB.categoria).all()
    return [r.categoria for r in result]
