# 📦 Sistema de Gestión de Productos

Sistema completo de inventario para PyMEs con panel de control, CRUD de productos y generación de reportes PDF.

## Arquitectura

```
Frontend (Streamlit) ──HTTP──► Backend (FastAPI) ──ORM──► PostgreSQL
                                                  └──► ReportLab (PDF)
```

| Capa       | Tecnología           | Puerto |
|------------|----------------------|--------|
| Frontend   | Streamlit            | 8501   |
| Backend    | FastAPI + Uvicorn    | 8000   |
| Base datos | PostgreSQL           | 5432   |

---

## Requisitos Previos

- Python 3.10+
- PostgreSQL 14+ corriendo localmente (o en Docker)

---

## 🐳 Ejecución con Docker (Recomendado)

Para una configuración rápida y sin complicaciones, puedes usar Docker Desktop.

### Paso 1: Requisitos
- Tener instalado **Docker Desktop** (App de escritorio).
- Asegurarte de que Docker esté corriendo.

### Paso 2: Levantar el proyecto
Desde la carpeta raíz del proyecto (`product_manager/`), ejecuta:

```bash
docker-compose up --build
```

Este comando:
1. Creará un contenedor con **PostgreSQL** y cargará automáticamente el esquema.
2. Construirá y levantará el **Backend (FastAPI)**.
3. Construirá y levantará el **Frontend (Streamlit)**.

### Paso 3: Acceder a las aplicaciones
- **Frontend**: http://localhost:8501
- **Backend (Docs)**: http://localhost:8000/docs

---

## 1. Configurar la Base de Datos (Manual)

```bash
# Crear la base de datos
psql -U postgres -c "CREATE DATABASE product_manager;"

# Ejecutar el esquema (crea tabla, índices y datos de ejemplo)
psql -U postgres -d product_manager -f database/schema.sql
```

---

## 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional, editar .env)
cp ../.env.example .env
# Editar .env con tus credenciales de PostgreSQL

# Iniciar el servidor
python main.py
# o:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 3. Configurar el Frontend

```bash
cd frontend

# Crear entorno virtual (separado del backend)
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar Streamlit
streamlit run app.py
```

La aplicación estará disponible en: http://localhost:8501

---

## Variables de Entorno

Crear archivo `.env` en la carpeta `backend/`:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/product_manager
```

---

## Estructura del Proyecto

```
product_manager/
├── backend/
│   ├── main.py          # Servidor FastAPI + todos los endpoints
│   ├── models.py        # Modelos ORM (SQLAlchemy) + esquemas (Pydantic)
│   ├── crud.py          # Lógica de operaciones de base de datos
│   ├── database.py      # Configuración de conexión PostgreSQL
│   └── requirements.txt
│
├── frontend/
│   ├── app.py               # App principal Streamlit (navegación)
│   ├── pdf_reports.py       # Generador de PDFs con ReportLab
│   ├── pages/
│   │   ├── 1_Dashboard.py   # KPIs, gráficos Plotly, bajo stock
│   │   ├── 2_Productos.py   # CRUD completo
│   │   └── 3_Reportes.py    # Generación de PDFs
│   └── requirements.txt
│
├── database/
│   └── schema.sql       # DDL + datos de ejemplo
│
└── README.md
```

---

## Endpoints de la API

### Productos
| Método | Endpoint                     | Descripción                    |
|--------|------------------------------|--------------------------------|
| GET    | /productos                   | Listar (con search, categoria) |
| GET    | /productos/{id}              | Obtener uno                    |
| GET    | /productos/categorias        | Lista de categorías            |
| POST   | /productos                   | Crear                          |
| PUT    | /productos/{id}              | Actualizar                     |
| DELETE | /productos/{id}              | Eliminar                       |

### Estadísticas
| Método | Endpoint                     | Descripción               |
|--------|------------------------------|---------------------------|
| GET    | /stats/dashboard             | KPIs principales          |
| GET    | /stats/categorias            | Stats agrupadas           |
| GET    | /stats/bajo-stock            | Productos a reordenar     |

---

## Funcionalidades

### 📊 Dashboard
- Total de productos, valor de inventario, bajo stock, margen promedio
- Gráfico de barras: Top 10 categorías
- Gráfico de pastel: Distribución por valor
- Tabla de productos que requieren reorden

### 📋 Gestión de Productos
- Tabla con búsqueda en tiempo real (SKU, nombre, proveedor, descripción)
- Filtro por categoría y estado de stock
- Crear producto con validación completa
- Editar producto (todos los campos)
- Eliminar con confirmación obligatoria
- Exportar a CSV

### 📄 Reportes PDF
- **Inventario Actual**: Tabla horizontal A4 con todos los productos, filtrable por categoría
- **Análisis Estratégico**: KPIs + distribución por categoría + productos a reordenar

---

## Notas de Desarrollo

- El frontend usa `st.cache_data(ttl=30)` para caché de 30 segundos
- El botón "Actualizar" limpia el caché explícitamente
- La URL del backend puede cambiarse en el sidebar (configuración)
- Los PDFs se generan en memoria (sin escribir a disco)
- Trigger SQL actualiza `fecha_ultima_actualizacion` automáticamente
