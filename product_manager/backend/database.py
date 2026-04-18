"""
database.py - Configuración de conexión a PostgreSQL con SQLAlchemy
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Obtener la ruta del archivo .env en el directorio raíz del proyecto
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# URL local de respaldo (Docker)
LOCAL_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/product_manager"

# URL principal: prioriza DATABASE_URL (por ejemplo Supabase)
PRIMARY_DATABASE_URL = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL)

# URL de respaldo: configurable, por defecto PostgreSQL local en Docker
FALLBACK_DATABASE_URL = os.getenv("DATABASE_URL_FALLBACK", LOCAL_DATABASE_URL)

# Fallback opcional: solo se usa cuando se habilita explícitamente
ENABLE_DB_FALLBACK = os.getenv("ENABLE_DB_FALLBACK", "false").lower() == "true"


def _create_engine(database_url: str):
    """Crear motor SQLAlchemy con configuración de pool estándar."""
    return create_engine(
        database_url,
        pool_pre_ping=True,      # Verifica conexiones antes de usarlas
        pool_size=10,            # Número de conexiones en el pool
        max_overflow=20,         # Conexiones adicionales permitidas
        echo=False               # True para ver SQL en consola (debug)
    )


def _is_connection_available(db_engine) -> bool:
    """Valida disponibilidad de conexión con una consulta simple."""
    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# Crear motor principal y activar fallback automÃ¡tico solo si estÃ¡ habilitado
engine = _create_engine(PRIMARY_DATABASE_URL)

if ENABLE_DB_FALLBACK and PRIMARY_DATABASE_URL != FALLBACK_DATABASE_URL and not _is_connection_available(engine):
    fallback_engine = _create_engine(FALLBACK_DATABASE_URL)
    if _is_connection_available(fallback_engine):
        engine = fallback_engine
    else:
        raise RuntimeError(
            "No se pudo conectar ni a la base principal (DATABASE_URL) ni al respaldo "
            "(DATABASE_URL_FALLBACK)."
        )

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos ORM
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos.
    Uso en FastAPI como dependencia (Depends).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
