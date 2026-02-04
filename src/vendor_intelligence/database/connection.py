"""
Database Connection Management

Handles:
    - SQLAlchemy engine creation with connection pooling
    - Session management for FastAPI
    - Database initialization
    - Connection health checks
    - Lifecycle event logging

SECURITY:
    - All connection details loaded from environment variables
    - No hardcoded credentials

Author: Group 2 - Vendor Intelligence Team
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError
from typing import Generator, Dict, Any
import logging

from vendor_intelligence.core.config import settings
from vendor_intelligence.database.base import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# CREATE SQLALCHEMY ENGINE
# ============================================

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DB_ECHO,
)

logger.info(f"Database engine created: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")


# ============================================
# EVENT LISTENERS
# ============================================

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Event listener: Called when new database connection is established
    
    Args:
        dbapi_conn: Database API connection
        connection_record: Connection record object
    """
    logger.info("📊 New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Event listener: Called when connection is checked out from pool
    
    Validates connection is still alive using ping
    
    Args:
        dbapi_conn: Database API connection
        connection_record: Connection record object
        connection_proxy: Connection proxy object
        
    Raises:
        DisconnectionError: If connection ping fails
    """
    try:
        # Test if connection is still alive
        dbapi_conn.ping(False)
    except Exception as e:
        logger.warning(f"⚠️  Connection ping failed: {e}")
        # Raise DisconnectionError to trigger connection refresh
        raise DisconnectionError()


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Event listener: Called when connection is returned to pool
    
    Args:
        dbapi_conn: Database API connection
        connection_record: Connection record object
    """
    logger.debug("Database connection returned to pool")


# ============================================
# SESSION FACTORY
# ============================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


# ============================================
# FASTAPI DEPENDENCY
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions
    
    Provides a database session that:
        - Auto-commits on success
        - Auto-rolls back on error
        - Auto-closes when done
    
    Usage in FastAPI:
        @app.get("/vendors")
        def get_vendors(db: Session = Depends(get_db)):
            vendors = db.query(Vendor).all()
            return vendors
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        # In calculator:
        async def calculate_pickup_rate(
            vendor_id: int,
            db: Session = Depends(get_db)
        ):
            trips = db.query(Trip).filter(Trip.vendor_id == vendor_id).all()
            # ... calculate ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"❌ Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db() -> None:
    """
    Initialize database by creating all tables
    
    This function:
        1. Imports all models (to register with SQLAlchemy)
        2. Creates all tables if they don't exist
        3. Logs success or failure
    
    Should be called once at application startup
    
    Raises:
        Exception: If database initialization fails
        
    Example:
        # In main.py startup:
        @app.on_event("startup")
        async def startup():
            init_db()
    """
    try:
        logger.info("📊 Initializing database...")
        
        # Import all models to register them with Base
        # IMPORTANT: Models must be imported before create_all()
        from src.vendor_intelligence.models import vendor, trip
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully")
        
        # Log created tables
        table_names = [table.name for table in Base.metadata.sorted_tables]
        logger.info(f"Tables: {', '.join(table_names)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


# ============================================
# CONNECTION HEALTH CHECK
# ============================================

def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    
    Attempts to execute a simple query (SELECT 1)
    
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        if check_db_connection():
            print("Database is accessible")
        else:
            print("Cannot connect to database")
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection is healthy")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {e}")
        return False


# ============================================
# CONNECTION POOL STATISTICS
# ============================================

def get_db_stats() -> Dict[str, Any]:
    """
    Get current database connection pool statistics
    
    Useful for:
        - Monitoring connection pool usage
        - Debugging connection issues
        - Performance tuning
    
    Returns:
        dict: Dictionary containing pool statistics
        
    Example:
        stats = get_db_stats()
        print(f"Pool size: {stats['pool_size']}")
        print(f"Checked out: {stats['checked_out']}")
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow(),
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "configured_pool_size": settings.DB_POOL_SIZE
    }


# ============================================
# CLEANUP
# ============================================

def close_db_connection() -> None:
    """
    Close all database connections and dispose of connection pool
    
    Should be called when application shuts down
    
    Example:
        # In main.py shutdown:
        @app.on_event("shutdown")
        async def shutdown():
            close_db_connection()
    """
    try:
        engine.dispose()
        logger.info("👋 Database connection pool disposed")
    except Exception as e:
        logger.error(f"❌ Error disposing database connection pool: {e}")