"""
pages/1_Dashboard.py - Panel principal con KPIs y visualizaciones
"""
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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

@st.cache_data(ttl=30)
def fetch_dashboard_stats():
    try:
        r = requests.get(f"{API_URL}/stats/dashboard", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=30)
def fetch_categorias_stats():
    try:
        r = requests.get(f"{API_URL}/stats/categorias", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=30)
def fetch_bajo_stock():
    try:
        r = requests.get(f"{API_URL}/stats/bajo-stock", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

PALETA = [
    "#2E86AB", "#1E3A5F", "#3BB273", "#F4A259",
    "#E84855", "#8338EC", "#06A77D", "#FF6B6B",
    "#4ECDC4", "#45B7D1"
]

# ─────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
    <h1 style="margin:0; color:#1E3A5F;">📊 Dashboard</h1>
    <p style="margin:0.3rem 0 0; color:#718096; font-size:0.9rem;">
        Indicadores clave y visualizaciones en tiempo real
    </p>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

# ─────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────

stats, err_stats = fetch_dashboard_stats()

if err_stats:
    st.error(f"⚠ No se pudo conectar al backend: {err_stats}")
    st.info("Asegúrate de que FastAPI está corriendo en " + API_URL)
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📦 Productos",
        stats.get("total_productos", 0),
        help="Total de productos únicos en el sistema"
    )
with col2:
    valor = stats.get("valor_total_inventario", 0)
    st.metric(
        "💰 Valor Inventario",
        f"S/ {valor:,.0f}",
        help="Suma de stock_actual × precio_compra"
    )
with col3:
    bajo = stats.get("productos_bajo_stock", 0)
    delta_color = "inverse" if bajo > 0 else "normal"
    st.metric(
        "⚠ Bajo Stock",
        bajo,
        delta=f"Requieren reorden" if bajo > 0 else "Todo OK",
        delta_color=delta_color,
        help="Productos con stock_actual < stock_minimo"
    )
with col4:
    st.metric(
        "🏷 Categorías",
        stats.get("total_categorias", 0),
        help="Número de categorías activas"
    )
with col5:
    margen = stats.get("margen_promedio_pct", 0)
    st.metric(
        "📈 Margen Prom.",
        f"{margen:.1f}%",
        help="Margen promedio: (precio_venta - precio_compra) / precio_compra"
    )

if stats.get("producto_mas_valioso"):
    st.markdown(f"""
    <div style="background:#EBF8FF; border:1px solid #BEE3F8; border-radius:8px;
                padding:0.7rem 1rem; margin:0.8rem 0; font-size:0.9rem; color:#2C5282;">
        🏆 <strong>Producto más valioso en inventario:</strong> {stats['producto_mas_valioso']}
        &nbsp;·&nbsp; S/ {float(stats.get('valor_producto_top', 0)):,.2f}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# GRÁFICOS
# ─────────────────────────────────────────────────

cat_data, err_cat = fetch_categorias_stats()

if cat_data:
    df_cat = pd.DataFrame(cat_data)

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        st.markdown("#### 📊 Top 10 Categorías por Cantidad de Productos")
        top10 = df_cat.nlargest(10, "total_productos").sort_values("total_productos")

        fig_bar = go.Figure(go.Bar(
            x=top10["total_productos"],
            y=top10["categoria"],
            orientation="h",
            marker=dict(
                color=top10["total_productos"],
                colorscale=[[0, "#BEE3F8"], [1, "#1E3A5F"]],
                showscale=False
            ),
            text=top10["total_productos"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Productos: %{x}<extra></extra>"
        ))
        fig_bar.update_layout(
            height=350,
            margin=dict(l=10, r=30, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", size=12),
            xaxis=dict(gridcolor="#EDF2F7", gridwidth=1),
            yaxis=dict(gridcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.markdown("#### 🥧 Distribución por Valor de Inventario")

        fig_pie = go.Figure(go.Pie(
            labels=df_cat["categoria"],
            values=df_cat["valor_inventario"],
            hole=0.45,
            marker=dict(colors=PALETA[:len(df_cat)]),
            textinfo="percent+label",
            textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>S/ %{value:,.2f}<br>%{percent}<extra></extra>"
        ))
        fig_pie.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            showlegend=False,
            annotations=[dict(
                text="Valor<br>Inv.",
                x=0.5, y=0.5,
                font=dict(size=11, color="#718096"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico de valor de inventario por categoría
    st.markdown("#### 💵 Valor de Inventario por Categoría")
    df_sorted = df_cat.sort_values("valor_inventario", ascending=False)
    fig_val = px.bar(
        df_sorted, x="categoria", y="valor_inventario",
        color="valor_inventario",
        color_continuous_scale=["#BEE3F8", "#2E86AB", "#1E3A5F"],
        labels={"categoria": "Categoría", "valor_inventario": "Valor (S/)"},
        text_auto=".2s"
    )
    fig_val.update_traces(textfont_size=10, textangle=0, textposition="outside")
    fig_val.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False,
        font=dict(family="Inter"),
        yaxis=dict(gridcolor="#EDF2F7"),
        xaxis=dict(title=None)
    )
    st.plotly_chart(fig_val, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# TABLA DE BAJO STOCK
# ─────────────────────────────────────────────────

st.markdown("#### 🚨 Productos que Necesitan Reorden")

bajo_stock_data, err_bs = fetch_bajo_stock()

if err_bs:
    st.error(f"Error al cargar datos de bajo stock: {err_bs}")
elif not bajo_stock_data:
    st.markdown("""
    <div class="alert-success">
        ✅ <strong>¡Excelente!</strong> Todos los productos tienen niveles de stock adecuados.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="alert-danger">
        ⚠ Se encontraron <strong>{len(bajo_stock_data)}</strong> productos
        con stock por debajo del mínimo establecido.
    </div>
    """, unsafe_allow_html=True)

    df_bs = pd.DataFrame(bajo_stock_data)
    df_bs = df_bs.rename(columns={
        "sku": "SKU",
        "nombre": "Producto",
        "categoria": "Categoría",
        "stock_actual": "Stock Actual",
        "stock_minimo": "Stock Mínimo",
        "deficit": "Déficit",
        "proveedor": "Proveedor"
    })
    df_bs = df_bs.drop(columns=["id"], errors="ignore")
    df_bs = df_bs.sort_values("Déficit", ascending=False)

    st.dataframe(
        df_bs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Déficit": st.column_config.NumberColumn(
                "Déficit", format="%d ⚠",
                help="Unidades que faltan para llegar al stock mínimo"
            ),
            "Stock Actual": st.column_config.NumberColumn("Stock Actual", format="%d"),
            "Stock Mínimo": st.column_config.NumberColumn("Stock Mínimo", format="%d"),
        }
    )
