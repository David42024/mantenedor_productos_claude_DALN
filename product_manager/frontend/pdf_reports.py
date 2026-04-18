"""
pdf_reports.py - Generación de reportes PDF con ReportLab
Uso: importar en app.py de Streamlit
"""
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF


# ============================================================
# PALETA DE COLORES CORPORATIVA
# ============================================================
COLOR_PRIMARY    = colors.HexColor("#1E3A5F")   # Azul marino
COLOR_SECONDARY  = colors.HexColor("#2E86AB")   # Azul medio
COLOR_ACCENT     = colors.HexColor("#E84855")   # Rojo acento
COLOR_SUCCESS    = colors.HexColor("#3BB273")   # Verde
COLOR_WARNING    = colors.HexColor("#F4A259")   # Naranja
COLOR_LIGHT      = colors.HexColor("#F0F4F8")   # Gris claro
COLOR_WHITE      = colors.white
COLOR_TEXT       = colors.HexColor("#2D3748")   # Gris oscuro
COLOR_MUTED      = colors.HexColor("#718096")   # Gris medio


def _build_styles():
    """Construir estilos de párrafo personalizados."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "TituloReporte",
        parent=styles["Title"],
        fontSize=22, fontName="Helvetica-Bold",
        textColor=COLOR_PRIMARY, alignment=TA_CENTER,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "SubtituloReporte",
        parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=COLOR_MUTED, alignment=TA_CENTER,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        "SeccionTitulo",
        parent=styles["Heading2"],
        fontSize=13, fontName="Helvetica-Bold",
        textColor=COLOR_PRIMARY, spaceBefore=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "KPILabel",
        parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=COLOR_MUTED, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "KPIValue",
        parent=styles["Normal"],
        fontSize=18, fontName="Helvetica-Bold",
        textColor=COLOR_SECONDARY, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "Nota",
        parent=styles["Normal"],
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=COLOR_MUTED
    ))
    styles.add(ParagraphStyle(
        "CeldaTabla",
        parent=styles["Normal"],
        fontSize=8, fontName="Helvetica",
        textColor=COLOR_TEXT
    ))
    return styles


def _header_section(styles, titulo: str, subtitulo: str) -> List:
    """Construir encabezado del reporte."""
    elementos = []

    # Línea decorativa superior
    elementos.append(HRFlowable(
        width="100%", thickness=4,
        color=COLOR_PRIMARY, spaceAfter=10
    ))

    elementos.append(Paragraph("📦 GESTIÓN DE PRODUCTOS", styles["SubtituloReporte"]))
    elementos.append(Paragraph(titulo, styles["TituloReporte"]))
    elementos.append(Paragraph(subtitulo, styles["SubtituloReporte"]))
    elementos.append(Spacer(1, 0.2 * cm))

    # Fecha y hora de generación
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"Generado: {fecha_str}", styles["Nota"]))
    elementos.append(HRFlowable(
        width="100%", thickness=1,
        color=COLOR_SECONDARY, spaceBefore=8, spaceAfter=12
    ))
    return elementos


def _kpi_table(kpis: List[Dict], styles) -> Table:
    """Crear tabla de KPIs visuales en fila."""
    header_row = [Paragraph(k["label"], styles["KPILabel"]) for k in kpis]
    value_row  = [Paragraph(k["value"], styles["KPIValue"]) for k in kpis]

    tabla = Table(
        [header_row, value_row],
        colWidths=[4.5 * cm] * len(kpis),
        rowHeights=[0.8 * cm, 1.2 * cm]
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), COLOR_LIGHT),
        ("BACKGROUND",    (0, 1), (-1, 1), colors.white),
        ("BOX",           (0, 0), (-1, -1), 0.5, COLOR_SECONDARY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E0")),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tabla


# ============================================================
# REPORTE 1: INVENTARIO ACTUAL
# ============================================================

def generar_reporte_inventario(
    productos: List[Dict],
    categoria_filtro: Optional[str] = None
) -> bytes:
    """
    Genera PDF con listado detallado del inventario actual.
    Retorna bytes del PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Inventario Actual"
    )

    styles = _build_styles()
    elementos = []

    # Encabezado
    subtitulo = f"Categoría: {categoria_filtro}" if categoria_filtro else "Todos los productos"
    elementos += _header_section(styles, "LISTADO DEL INVENTARIO ACTUAL", subtitulo)

    # Resumen estadístico
    total_prods  = len(productos)
    valor_total  = sum(float(p.get("stock_actual", 0)) * float(p.get("precio_compra", 0)) for p in productos)
    bajo_stock_n = sum(1 for p in productos if int(p.get("stock_actual", 0)) < int(p.get("stock_minimo", 0)))

    kpis = [
        {"label": "Total Productos",           "value": str(total_prods)},
        {"label": "Valor Total Inventario",    "value": f"S/ {valor_total:,.2f}"},
        {"label": "Productos Bajo Stock",      "value": str(bajo_stock_n)},
        {"label": "Categorías",                "value": str(len(set(p.get("categoria", "") for p in productos)))},
    ]
    elementos.append(_kpi_table(kpis, styles))
    elementos.append(Spacer(1, 0.5 * cm))

    # Tabla de productos
    elementos.append(Paragraph("Detalle de Productos", styles["SeccionTitulo"]))

    col_headers = ["SKU", "Nombre", "Categoría", "Proveedor",
                   "P. Compra", "P. Venta", "Stock", "Stock Mín.", "Valor Inv.", "Estado"]
    col_widths  = [2.5*cm, 6*cm, 3*cm, 4*cm, 2.2*cm, 2.2*cm, 1.8*cm, 2*cm, 2.5*cm, 2*cm]

    header_cells = [Paragraph(f"<b>{h}</b>", styles["CeldaTabla"]) for h in col_headers]
    data_rows    = [header_cells]

    for p in productos:
        stock_act  = int(p.get("stock_actual", 0))
        stock_min  = int(p.get("stock_minimo", 0))
        precio_c   = float(p.get("precio_compra", 0))
        precio_v   = float(p.get("precio_venta", 0))
        valor_inv  = stock_act * precio_c
        estado     = "⚠ BAJO" if stock_act < stock_min else ("✓ OK" if stock_act > 0 else "✗ AGOTADO")

        row = [
            Paragraph(str(p.get("sku", "")),         styles["CeldaTabla"]),
            Paragraph(str(p.get("nombre", "")),       styles["CeldaTabla"]),
            Paragraph(str(p.get("categoria", "")),    styles["CeldaTabla"]),
            Paragraph(str(p.get("proveedor", "-")),   styles["CeldaTabla"]),
            Paragraph(f"S/ {precio_c:.2f}",           styles["CeldaTabla"]),
            Paragraph(f"S/ {precio_v:.2f}",           styles["CeldaTabla"]),
            Paragraph(str(stock_act),                 styles["CeldaTabla"]),
            Paragraph(str(stock_min),                 styles["CeldaTabla"]),
            Paragraph(f"S/ {valor_inv:,.2f}",         styles["CeldaTabla"]),
            Paragraph(estado,                         styles["CeldaTabla"]),
        ]
        data_rows.append(row)

    tabla_productos = Table(data_rows, colWidths=col_widths, repeatRows=1)
    tabla_productos.setStyle(TableStyle([
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        # Filas alternas
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_LIGHT]),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E0")),
        ("BOX",           (0, 0), (-1, -1), 1, COLOR_SECONDARY),
    ]))

    elementos.append(tabla_productos)

    # Pie de página informativo
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_MUTED))
    elementos.append(Paragraph(
        f"Reporte generado automáticamente por el Sistema de Gestión de Productos | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Nota"]
    ))

    doc.build(elementos)
    return buffer.getvalue()


# ============================================================
# REPORTE 2: ANÁLISIS DE INVENTARIO Y BAJO STOCK
# ============================================================

def generar_reporte_analisis(
    stats: Dict,
    categorias: List[Dict],
    bajo_stock: List[Dict]
) -> bytes:
    """
    Genera PDF con KPIs, análisis por categoría y productos a reordenar.
    Retorna bytes del PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Análisis de Inventario y Bajo Stock"
    )

    styles = _build_styles()
    elementos = []

    # Encabezado
    fecha_str = datetime.now().strftime("%B %Y")
    elementos += _header_section(
        styles,
        "ANÁLISIS DE INVENTARIO Y BAJO STOCK",
        f"Informe Estratégico · {fecha_str}"
    )

    # ---- SECCIÓN 1: KPIs ----
    elementos.append(Paragraph("1. Indicadores Clave de Desempeño (KPIs)", styles["SeccionTitulo"]))

    kpis = [
        {"label": "Productos Únicos",        "value": str(stats.get("total_productos", 0))},
        {"label": "Valor Inventario",         "value": f"S/ {float(stats.get('valor_total_inventario', 0)):,.0f}"},
        {"label": "Bajo Stock",               "value": str(stats.get("productos_bajo_stock", 0))},
        {"label": "Categorías",               "value": str(stats.get("total_categorias", 0))},
        {"label": "Margen Promedio",          "value": f"{float(stats.get('margen_promedio_pct', 0)):.1f}%"},
    ]
    elementos.append(_kpi_table(kpis, styles))

    # Producto más valioso
    if stats.get("producto_mas_valioso"):
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph(
            f"🏆 Producto más valioso en inventario: <b>{stats['producto_mas_valioso']}</b> "
            f"(S/ {float(stats.get('valor_producto_top', 0)):,.2f})",
            styles["Nota"]
        ))

    elementos.append(Spacer(1, 0.5 * cm))

    # ---- SECCIÓN 2: DISTRIBUCIÓN POR CATEGORÍA ----
    elementos.append(Paragraph("2. Distribución por Categoría", styles["SeccionTitulo"]))

    cat_headers = ["Categoría", "Productos", "Stock Total", "Valor Inventario", "% del Total"]
    cat_widths  = [5 * cm, 3 * cm, 3 * cm, 4.5 * cm, 3 * cm]
    val_total   = sum(float(c.get("valor_inventario", 0)) for c in categorias)

    cat_header_row = [Paragraph(f"<b>{h}</b>", styles["CeldaTabla"]) for h in cat_headers]
    cat_rows = [cat_header_row]

    for c in categorias:
        val_cat = float(c.get("valor_inventario", 0))
        pct     = (val_cat / val_total * 100) if val_total > 0 else 0
        cat_rows.append([
            Paragraph(str(c.get("categoria", "")),                          styles["CeldaTabla"]),
            Paragraph(str(c.get("total_productos", 0)),                     styles["CeldaTabla"]),
            Paragraph(str(c.get("stock_total", 0)),                         styles["CeldaTabla"]),
            Paragraph(f"S/ {val_cat:,.2f}",                                 styles["CeldaTabla"]),
            Paragraph(f"{pct:.1f}%",                                        styles["CeldaTabla"]),
        ])

    # Fila total
    cat_rows.append([
        Paragraph("<b>TOTAL</b>",                                           styles["CeldaTabla"]),
        Paragraph(f"<b>{sum(c.get('total_productos',0) for c in categorias)}</b>", styles["CeldaTabla"]),
        Paragraph(f"<b>{sum(c.get('stock_total',0) for c in categorias)}</b>",     styles["CeldaTabla"]),
        Paragraph(f"<b>S/ {val_total:,.2f}</b>",                            styles["CeldaTabla"]),
        Paragraph("<b>100%</b>",                                            styles["CeldaTabla"]),
    ])

    tabla_cat = Table(cat_rows, colWidths=cat_widths, repeatRows=1)
    tabla_cat.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_SECONDARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [colors.white, COLOR_LIGHT]),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#EBF4FF")),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E0")),
        ("BOX",           (0, 0), (-1, -1), 1, COLOR_SECONDARY),
    ]))
    elementos.append(tabla_cat)
    elementos.append(Spacer(1, 0.5 * cm))

    # ---- SECCIÓN 3: PRODUCTOS A REORDENAR ----
    elementos.append(Paragraph("3. Productos que Requieren Reorden Urgente", styles["SeccionTitulo"]))

    if not bajo_stock:
        elementos.append(Paragraph(
            "✅ Todos los productos tienen niveles de stock adecuados.", styles["Nota"]
        ))
    else:
        bs_headers = ["SKU", "Producto", "Categoría", "Stock Actual", "Stock Mínimo", "Déficit", "Proveedor"]
        bs_widths  = [2.5*cm, 5.5*cm, 3*cm, 2.5*cm, 2.5*cm, 2*cm, 4.5*cm]

        bs_header_row = [Paragraph(f"<b>{h}</b>", styles["CeldaTabla"]) for h in bs_headers]
        bs_rows = [bs_header_row]

        for p in bajo_stock:
            deficit = int(p.get("deficit", 0))
            urgencia_color = COLOR_ACCENT if deficit > 5 else COLOR_WARNING

            bs_rows.append([
                Paragraph(str(p.get("sku", "")),          styles["CeldaTabla"]),
                Paragraph(str(p.get("nombre", "")),       styles["CeldaTabla"]),
                Paragraph(str(p.get("categoria", "")),    styles["CeldaTabla"]),
                Paragraph(str(p.get("stock_actual", 0)), styles["CeldaTabla"]),
                Paragraph(str(p.get("stock_minimo", 0)), styles["CeldaTabla"]),
                Paragraph(f"<b>{deficit}</b>",            styles["CeldaTabla"]),
                Paragraph(str(p.get("proveedor", "-")),   styles["CeldaTabla"]),
            ])

        tabla_bs = Table(bs_rows, colWidths=bs_widths, repeatRows=1)
        tabla_bs.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), COLOR_ACCENT),
            ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_WHITE),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
            ("ALIGN",         (3, 0), (5, -1), "CENTER"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF5F5")]),
            ("FONTSIZE",      (0, 1), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#FEB2B2")),
            ("BOX",           (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ]))
        elementos.append(tabla_bs)
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph(
            f"⚠ Se identificaron {len(bajo_stock)} productos con stock por debajo del mínimo establecido. "
            "Se recomienda contactar a los proveedores correspondientes de inmediato.",
            styles["Nota"]
        ))

    # Pie
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_MUTED))
    elementos.append(Paragraph(
        f"Informe generado automáticamente | Sistema de Gestión de Productos | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Nota"]
    ))

    doc.build(elementos)
    return buffer.getvalue()
