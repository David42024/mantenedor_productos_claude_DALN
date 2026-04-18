"""
pages/3_Reportes.py - Generación de reportes PDF
"""
import streamlit as st
import requests
import sys
import os
from datetime import datetime

# Importar el generador de PDFs desde el directorio padre del frontend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pdf_reports import generar_reporte_inventario, generar_reporte_analisis

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_URL = st.session_state.get("API_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


# ─────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────

def fetch_productos(categoria=None):
    params = {"limit": 5000}
    if categoria:
        params["categoria"] = categoria
    try:
        r = requests.get(f"{API_URL}/productos", params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def fetch_stats():
    try:
        r = requests.get(f"{API_URL}/stats/dashboard", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def fetch_categorias_stats():
    try:
        r = requests.get(f"{API_URL}/stats/categorias", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def fetch_bajo_stock():
    try:
        r = requests.get(f"{API_URL}/stats/bajo-stock", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def fetch_categorias():
    try:
        r = requests.get(f"{API_URL}/productos/categorias", timeout=5)
        r.raise_for_status()
        return r.json()
    except:
        return []


# ─────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
    <h1 style="margin:0; color:#1E3A5F;">📄 Reportes</h1>
    <p style="margin:0.3rem 0 0; color:#718096; font-size:0.9rem;">
        Generación de informes profesionales en formato PDF
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# TARJETAS DE REPORTES
# ─────────────────────────────────────────────────

st.markdown("### Reportes Disponibles")

rep1_col, rep2_col = st.columns(2)

# ══════════════════════════════════════════════════
# REPORTE 1: INVENTARIO ACTUAL
# ══════════════════════════════════════════════════

with rep1_col:
    st.markdown("""
    <div class="card" style="border-top: 4px solid #2E86AB; min-height: 160px;">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
            <span style="font-size:1.8rem;">📦</span>
            <div>
                <h3 style="margin:0; color:#1E3A5F; font-size:1rem;">Reporte Operacional</h3>
                <p style="margin:0; color:#718096; font-size:0.8rem;">Listado del Inventario Actual</p>
            </div>
        </div>
        <p style="color:#4A5568; font-size:0.85rem; margin-bottom:0.5rem;">
            Tabla detallada de todos los productos con SKU, nombre, stock, precios y valor total.
            Puede filtrarse por categoría antes de generar.
        </p>
        <div style="font-size:0.78rem; color:#718096;">
            📋 Incluye: tabla de productos · resumen estadístico · KPIs
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filtro por categoría
    categorias = ["Todas las categorías"] + fetch_categorias()
    cat_reporte1 = st.selectbox(
        "Filtrar por categoría",
        categorias,
        key="cat_reporte1",
        help="Selecciona una categoría para el reporte, o deja 'Todas' para incluir todo"
    )

    if st.button("📥 Generar Reporte de Inventario", use_container_width=True, key="btn_rep1"):
        with st.spinner("Generando PDF..."):
            cat_filtro = None if cat_reporte1 == "Todas las categorías" else cat_reporte1
            productos, err = fetch_productos(categoria=cat_filtro)

            if err:
                st.error(f"❌ Error al obtener datos: {err}")
            elif not productos:
                st.warning("No hay productos para generar el reporte.")
            else:
                try:
                    pdf_bytes = generar_reporte_inventario(
                        productos=productos,
                        categoria_filtro=cat_filtro
                    )
                    fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
                    cat_str   = f"_{cat_filtro.replace(' ', '_')}" if cat_filtro else ""
                    filename  = f"inventario_actual{cat_str}_{fecha_str}.pdf"

                    st.download_button(
                        label="⬇ Descargar PDF — Inventario Actual",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_rep1"
                    )
                    st.success(f"✅ PDF generado exitosamente con {len(productos)} productos.")
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {str(e)}")


# ══════════════════════════════════════════════════
# REPORTE 2: ANÁLISIS ESTRATÉGICO
# ══════════════════════════════════════════════════

with rep2_col:
    st.markdown("""
    <div class="card" style="border-top: 4px solid #E84855; min-height: 160px;">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
            <span style="font-size:1.8rem;">📊</span>
            <div>
                <h3 style="margin:0; color:#1E3A5F; font-size:1rem;">Reporte de Gestión</h3>
                <p style="margin:0; color:#718096; font-size:0.8rem;">Análisis de Inventario y Bajo Stock</p>
            </div>
        </div>
        <p style="color:#4A5568; font-size:0.85rem; margin-bottom:0.5rem;">
            Informe estratégico con KPIs del tablero, distribución por categoría y
            lista completa de productos que requieren reorden urgente.
        </p>
        <div style="font-size:0.78rem; color:#718096;">
            📊 Incluye: KPIs · análisis por categoría · tabla de bajo stock
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)

    if st.button("📥 Generar Análisis Estratégico", use_container_width=True, key="btn_rep2"):
        with st.spinner("Generando PDF con análisis completo..."):
            stats, err1       = fetch_stats()
            categorias_s, err2 = fetch_categorias_stats()
            bajo_stock, err3  = fetch_bajo_stock()

            errors = [e for e in [err1, err2, err3] if e]
            if errors:
                st.error(f"❌ Error al obtener datos: {'; '.join(errors)}")
            else:
                try:
                    pdf_bytes = generar_reporte_analisis(
                        stats=stats,
                        categorias=categorias_s,
                        bajo_stock=bajo_stock
                    )
                    fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
                    filename  = f"analisis_inventario_{fecha_str}.pdf"

                    st.download_button(
                        label="⬇ Descargar PDF — Análisis Estratégico",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_rep2"
                    )
                    st.success(
                        f"✅ PDF generado. "
                        f"{bajo_stock and len(bajo_stock) or 0} productos con bajo stock incluidos."
                    )
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {str(e)}")

# ─────────────────────────────────────────────────
# INFO
# ─────────────────────────────────────────────────

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="background:#F7FAFC; border:1px solid #E2E8F0; border-radius:10px;
            padding:1rem 1.25rem; font-size:0.85rem; color:#4A5568;">
    <strong style="color:#1E3A5F;">ℹ Acerca de los reportes</strong><br>
    Los PDFs se generan con <strong>ReportLab</strong> y están diseñados para impresión y distribución profesional.
    El Reporte de Inventario usa orientación <em>horizontal (landscape)</em> para mejor legibilidad.
    El Análisis Estratégico usa orientación <em>vertical (portrait)</em> estándar A4.
</div>
""", unsafe_allow_html=True)
