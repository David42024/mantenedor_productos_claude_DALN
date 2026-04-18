"""
app.py - Aplicación Streamlit: Sistema de Gestión de Productos
Punto de entrada principal con configuración y navegación.
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener la ruta del archivo .env en el directorio raíz del proyecto
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ============================================================
# CONFIGURACIÓN DE PÁGINA (debe ser lo primero)
# ============================================================
st.set_page_config(
    page_title="Gestión de Productos",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "**Sistema de Gestión de Productos** v1.0\nDesarrollado con FastAPI + Streamlit"
    }
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================
st.markdown("""
<style>
/* Importar fuente corporativa */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Variables de color */
:root {
    --primary:     #1E3A5F;
    --secondary:   #2E86AB;
    --accent:      #E84855;
    --success:     #3BB273;
    --warning:     #F4A259;
    --bg-light:    #F0F4F8;
    --text-main:   #2D3748;
    --text-muted:  #718096;
    --border:      #CBD5E0;
    --white:       #FFFFFF;
}

/* Fuente global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-main);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E3A5F 0%, #16304F 100%);
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #E2ECF7 !important;
}
section[data-testid="stSidebar"] .stRadio > label {
    color: #CBD5E0 !important;
    font-size: 0.85rem;
}

/* Métricas */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46,134,171,0.15);
}
[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--primary) !important;
}

/* DataFrames/Tablas */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
}

/* Botones primarios */
.stButton > button {
    background: var(--secondary) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--primary) !important;
}

/* Botones de peligro */
.btn-danger > button {
    background: var(--accent) !important;
}

/* Formularios */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Alertas personalizadas */
.alert-warning {
    background: #FFFBEB;
    border-left: 4px solid var(--warning);
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
}
.alert-danger {
    background: #FFF5F5;
    border-left: 4px solid var(--accent);
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
}
.alert-success {
    background: #F0FFF4;
    border-left: 4px solid var(--success);
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
}

/* Cards */
.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Título de página */
.page-header {
    border-bottom: 2px solid var(--secondary);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.2em 0.6em;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-danger  { background: #FED7D7; color: #C53030; }
.badge-success { background: #C6F6D5; color: #276749; }
.badge-warning { background: #FEEBC8; color: #C05621; }

/* Ocultar Streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background-color: var(--secondary) !important;
    color: white !important;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# PÁGINA PRINCIPAL DE BIENVENIDA
# ============================================================

# Logo y título en sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 1rem;">
        <div style="font-size:2.5rem;">📦</div>
        <div style="font-size:1.1rem; font-weight:700; color:white; margin-top:0.3rem;">
            Gestión de Productos
        </div>
        <div style="font-size:0.75rem; color:#94A3B8; margin-top:0.2rem;">
            Sistema de Inventario PyME
        </div>
    </div>
    <hr style="border-color:#2E4A6A; margin: 0.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;
                    color:#64748B; font-weight:600; margin-bottom:0.5rem;">
            NAVEGACIÓN
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("app.py",               label="🏠  Inicio",      )
    st.page_link("pages/1_Dashboard.py", label="📊  Dashboard",   )
    st.page_link("pages/2_Productos.py", label="📋  Productos",   )
    st.page_link("pages/3_Reportes.py",  label="📄  Reportes",    )

    st.markdown("<hr style='border-color:#2E4A6A; margin:1rem 0;'>", unsafe_allow_html=True)

    # Configuración de API
    st.markdown("""
    <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;
                color:#64748B; font-weight:600; margin-bottom:0.5rem;">
        CONFIGURACIÓN
    </div>
    """, unsafe_allow_html=True)

    api_url = st.text_input(
        "📍 URL de la API (Backend)",
        value=os.getenv("BACKEND_URL", "http://localhost:8000"),
        key="api_url_global",
        help="Cambia esto si tu backend corre en otro puerto o dominio."
    )
    if api_url:
        st.session_state["API_URL"] = api_url

    st.markdown("""
    <div style="margin-top:2rem; font-size:0.7rem; color:#475569; text-align:center;">
        v1.0.0 · FastAPI + Streamlit
    </div>
    """, unsafe_allow_html=True)


# Contenido de inicio
st.markdown("""
<div class="page-header">
    <h1 style="margin:0; color:#1E3A5F;">🏠 Sistema de Gestión de Productos</h1>
    <p style="margin:0.3rem 0 0; color:#718096; font-size:0.95rem;">
        Plataforma integrada de inventario para pequeñas y medianas empresas
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <div style="font-size:2rem; margin-bottom:0.5rem;">📊</div>
        <h3 style="margin:0 0 0.4rem; color:#1E3A5F;">Dashboard</h3>
        <p style="color:#718096; font-size:0.88rem; margin:0;">
            KPIs en tiempo real, gráficos de distribución por categoría
            y alertas de bajo stock.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div style="font-size:2rem; margin-bottom:0.5rem;">📋</div>
        <h3 style="margin:0 0 0.4rem; color:#1E3A5F;">Gestión de Productos</h3>
        <p style="color:#718096; font-size:0.88rem; margin:0;">
            CRUD completo: crear, visualizar, editar y eliminar productos
            con búsqueda y filtros avanzados.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div style="font-size:2rem; margin-bottom:0.5rem;">📄</div>
        <h3 style="margin:0 0 0.4rem; color:#1E3A5F;">Reportes PDF</h3>
        <p style="color:#718096; font-size:0.88rem; margin:0;">
            Genera reportes profesionales: inventario actual
            y análisis estratégico de bajo stock.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:1.5rem; padding:1rem 1.5rem; background:#EBF8FF;
            border-radius:10px; border-left:4px solid #2E86AB;">
    <strong style="color:#1E3A5F;">🚀 Inicio rápido:</strong>
    <span style="color:#4A5568; font-size:0.9rem;">
        Usa el menú lateral para navegar entre módulos. Asegúrate de que el backend
        FastAPI esté corriendo en <code>http://localhost:8000</code> antes de continuar.
    </span>
</div>
""", unsafe_allow_html=True)
