"""
Database Package
Provides database connection, session management, and base models

Exports:
    - engine: SQLAlchemy engine
    - SessionLocal: Session factory
    - get_db: FastAPI dependency for database sessions
    - Base: Declarative base for models
    - BaseModel: Base class with common attributes
    - TimestampMixin: Mixin for created_at/updated_at
"""
from vendor_intelligence.database.connection import (
    engine,
    SessionLocal,
    get_db,
    init_db,
    check_db_connection,
    close_db_connection,
    get_db_stats
)
from vendor_intelligence.database.base import (
    Base,
    BaseModel,
    TimestampMixin
)

__all__ = [
    # Connection
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "check_db_connection",
    "close_db_connection",
    "get_db_stats",
    
    # Base classes
    "Base",
    "BaseModel",
    "TimestampMixin",
]