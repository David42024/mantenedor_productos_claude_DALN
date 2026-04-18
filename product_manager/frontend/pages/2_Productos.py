"""
pages/2_Productos.py - CRUD completo de productos
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_URL = st.session_state.get("API_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


# ─────────────────────────────────────────────────
# HELPERS API
# ─────────────────────────────────────────────────

def api_get_productos(search=None, categoria=None, bajo_stock=False):
    params = {"limit": 1000}
    if search:    params["search"]     = search
    if categoria: params["categoria"]  = categoria
    if bajo_stock: params["bajo_stock"] = True
    try:
        r = requests.get(f"{API_URL}/productos", params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def api_get_categorias():
    try:
        r = requests.get(f"{API_URL}/productos/categorias", timeout=5)
        r.raise_for_status()
        return r.json()
    except:
        return []

def api_crear_producto(data):
    try:
        r = requests.post(f"{API_URL}/productos", json=data, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_actualizar_producto(id, data):
    try:
        r = requests.put(f"{API_URL}/productos/{id}", json=data, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_eliminar_producto(id):
    try:
        r = requests.delete(f"{API_URL}/productos/{id}", timeout=10)
        r.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        return False, detail
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
    <h1 style="margin:0; color:#1E3A5F;">📋 Gestión de Productos</h1>
    <p style="margin:0.3rem 0 0; color:#718096; font-size:0.9rem;">
        Crear, visualizar, editar y eliminar productos del inventario
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────

tab_lista, tab_nuevo, tab_editar = st.tabs(["📋 Listado", "➕ Nuevo Producto", "✏️ Editar/Eliminar"])


# ══════════════════════════════════════════════════
# TAB 1: LISTADO
# ══════════════════════════════════════════════════

with tab_lista:
    st.markdown("#### Filtros y Búsqueda")

    fcol1, fcol2, fcol3, fcol4 = st.columns([3, 2, 1.5, 1])
    with fcol1:
        search_term = st.text_input("🔍 Buscar", placeholder="SKU, nombre, proveedor...", key="search_lista")
    with fcol2:
        categorias_list = ["Todas"] + api_get_categorias()
        cat_filter = st.selectbox("Categoría", categorias_list, key="cat_filter_lista")
    with fcol3:
        solo_bajo_stock = st.checkbox("⚠ Solo bajo stock", key="bajo_stock_filter")
    with fcol4:
        st.markdown("<div style='margin-top:1.7rem;'>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar"):
            pass
        st.markdown("</div>", unsafe_allow_html=True)

    cat_selected = None if cat_filter == "Todas" else cat_filter
    productos, err = api_get_productos(
        search=search_term or None,
        categoria=cat_selected,
        bajo_stock=solo_bajo_stock
    )

    if err:
        st.error(f"Error al cargar productos: {err}")
    elif not productos:
        st.info("No se encontraron productos con los filtros aplicados.")
    else:
        st.markdown(f"<p style='color:#718096; font-size:0.85rem;'>Mostrando <strong>{len(productos)}</strong> producto(s)</p>", unsafe_allow_html=True)

        df = pd.DataFrame(productos)

        # Columnas visibles y renombradas
        cols_show = {
            "id": "ID",
            "sku": "SKU",
            "nombre": "Nombre",
            "categoria": "Categoría",
            "precio_compra": "P. Compra",
            "precio_venta": "P. Venta",
            "stock_actual": "Stock",
            "stock_minimo": "Stock Mín.",
            "proveedor": "Proveedor",
        }
        df_display = df[list(cols_show.keys())].rename(columns=cols_show)
        df_display["Estado"] = df.apply(
            lambda r: "⚠ BAJO" if r["stock_actual"] < r["stock_minimo"]
            else ("✗ AGOTADO" if r["stock_actual"] == 0 else "✓ OK"),
            axis=1
        )
        df_display["Valor Inv."] = df.apply(
            lambda r: round(r["stock_actual"] * r["precio_compra"], 2), axis=1
        )

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID":         st.column_config.NumberColumn("ID", width="small"),
                "P. Compra":  st.column_config.NumberColumn("P. Compra", format="S/ %.2f"),
                "P. Venta":   st.column_config.NumberColumn("P. Venta",  format="S/ %.2f"),
                "Stock":      st.column_config.NumberColumn("Stock",     format="%d"),
                "Stock Mín.": st.column_config.NumberColumn("Stock Mín.", format="%d"),
                "Valor Inv.": st.column_config.NumberColumn("Valor Inv.", format="S/ %.2f"),
                "Estado":     st.column_config.TextColumn("Estado", width="small"),
            },
            height=420
        )

        # Exportar a CSV
        csv_data = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Exportar a CSV",
            data=csv_data,
            file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="export_csv"
        )


# ══════════════════════════════════════════════════
# TAB 2: NUEVO PRODUCTO
# ══════════════════════════════════════════════════

with tab_nuevo:
    st.markdown("#### Crear Nuevo Producto")

    with st.form("form_nuevo_producto", clear_on_submit=True):
        st.markdown("**Información básica**")
        n_col1, n_col2 = st.columns(2)
        with n_col1:
            n_sku     = st.text_input("SKU *", placeholder="ELEC-001", help="Código único del producto")
            n_nombre  = st.text_input("Nombre *", placeholder="Laptop HP ProBook")
        with n_col2:
            n_cat     = st.text_input("Categoría *", placeholder="Electrónica")
            n_proveedor = st.text_input("Proveedor", placeholder="HP Enterprise")

        n_descripcion = st.text_area("Descripción", placeholder="Descripción detallada del producto...", height=80)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Precios y Stock**")

        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            n_precio_c = st.number_input("Precio Compra (S/) *", min_value=0.0, step=0.01, format="%.2f")
        with p_col2:
            n_precio_v = st.number_input("Precio Venta (S/) *",  min_value=0.0, step=0.01, format="%.2f")
        with p_col3:
            n_stock    = st.number_input("Stock Actual *",  min_value=0, step=1)
        with p_col4:
            n_stock_min = st.number_input("Stock Mínimo", min_value=0, step=1)

        submitted = st.form_submit_button("✅ Crear Producto", use_container_width=True)

    if submitted:
        # Validaciones básicas
        errors = []
        if not n_sku.strip():     errors.append("SKU es requerido")
        if not n_nombre.strip():  errors.append("Nombre es requerido")
        if not n_cat.strip():     errors.append("Categoría es requerida")
        if n_precio_v < n_precio_c:
            errors.append("El precio de venta no puede ser menor al de compra")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            payload = {
                "sku":           n_sku.strip().upper(),
                "nombre":        n_nombre.strip(),
                "descripcion":   n_descripcion.strip() or None,
                "categoria":     n_cat.strip(),
                "precio_compra": n_precio_c,
                "precio_venta":  n_precio_v,
                "stock_actual":  n_stock,
                "stock_minimo":  n_stock_min,
                "proveedor":     n_proveedor.strip() or None
            }
            result, err = api_crear_producto(payload)
            if err:
                st.error(f"❌ Error al crear producto: {err}")
            else:
                st.success(f"✅ Producto **{result['nombre']}** (ID: {result['id']}) creado exitosamente!")
                st.cache_data.clear()


# ══════════════════════════════════════════════════
# TAB 3: EDITAR / ELIMINAR
# ══════════════════════════════════════════════════

with tab_editar:
    st.markdown("#### Editar o Eliminar un Producto")

    # Selector de producto
    todos, err2 = api_get_productos()
    if err2:
        st.error(f"Error al cargar productos: {err2}")
        st.stop()

    if not todos:
        st.info("No hay productos disponibles.")
    else:
        opciones = {f"[{p['id']}] {p['sku']} — {p['nombre']}": p for p in todos}
        seleccion = st.selectbox("Seleccionar Producto", list(opciones.keys()), key="select_editar")
        producto_sel = opciones[seleccion]

        st.markdown("<hr>", unsafe_allow_html=True)

        edit_tab, del_tab = st.tabs(["✏️ Editar", "🗑️ Eliminar"])

        # ---- EDITAR ----
        with edit_tab:
            with st.form("form_editar_producto"):
                st.markdown("**Información básica**")
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    e_sku    = st.text_input("SKU",    value=producto_sel["sku"])
                    e_nombre = st.text_input("Nombre", value=producto_sel["nombre"])
                with e_col2:
                    e_cat       = st.text_input("Categoría", value=producto_sel["categoria"])
                    e_proveedor = st.text_input("Proveedor", value=producto_sel.get("proveedor") or "")

                e_descripcion = st.text_area(
                    "Descripción",
                    value=producto_sel.get("descripcion") or "",
                    height=80
                )

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("**Precios y Stock**")

                ep1, ep2, ep3, ep4 = st.columns(4)
                with ep1:
                    e_pc = st.number_input("P. Compra", value=float(producto_sel["precio_compra"]),
                                           min_value=0.0, step=0.01, format="%.2f")
                with ep2:
                    e_pv = st.number_input("P. Venta",  value=float(producto_sel["precio_venta"]),
                                           min_value=0.0, step=0.01, format="%.2f")
                with ep3:
                    e_sa = st.number_input("Stock Actual",  value=producto_sel["stock_actual"], min_value=0)
                with ep4:
                    e_sm = st.number_input("Stock Mínimo",  value=producto_sel["stock_minimo"], min_value=0)

                edit_submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)

            if edit_submitted:
                errs = []
                if not e_sku.strip():    errs.append("SKU no puede estar vacío")
                if not e_nombre.strip(): errs.append("Nombre no puede estar vacío")
                if e_pv < e_pc:          errs.append("Precio de venta no puede ser menor al de compra")
                if errs:
                    for e in errs:
                        st.error(f"❌ {e}")
                else:
                    payload = {
                        "sku":           e_sku.strip().upper(),
                        "nombre":        e_nombre.strip(),
                        "descripcion":   e_descripcion.strip() or None,
                        "categoria":     e_cat.strip(),
                        "precio_compra": e_pc,
                        "precio_venta":  e_pv,
                        "stock_actual":  e_sa,
                        "stock_minimo":  e_sm,
                        "proveedor":     e_proveedor.strip() or None
                    }
                    result, err = api_actualizar_producto(producto_sel["id"], payload)
                    if err:
                        st.error(f"❌ Error: {err}")
                    else:
                        st.success(f"✅ Producto actualizado correctamente!")
                        st.cache_data.clear()
                        st.rerun()

        # ---- ELIMINAR ----
        with del_tab:
            st.markdown(f"""
            <div class="alert-danger">
                🗑️ Estás a punto de eliminar el producto:<br>
                <strong>{producto_sel['sku']} — {producto_sel['nombre']}</strong><br>
                <small>Esta acción <strong>no se puede deshacer</strong>.</small>
            </div>
            """, unsafe_allow_html=True)

            confirmar = st.checkbox(
                f"Confirmo que quiero eliminar '{producto_sel['nombre']}' (ID: {producto_sel['id']})",
                key="confirm_delete"
            )

            if st.button("🗑️ Eliminar Producto", disabled=not confirmar, key="btn_delete"):
                ok, err = api_eliminar_producto(producto_sel["id"])
                if err:
                    st.error(f"❌ Error al eliminar: {err}")
                else:
                    st.success(f"✅ Producto eliminado correctamente.")
                    st.cache_data.clear()
                    st.rerun()
