"""
Configuration Settings for Vendor Intelligence Application

SECURITY NOTICE:
- All sensitive values are loaded from .env file ONLY
- NO default values for database credentials
- .env file is in .gitignore and NEVER committed to Git
- Each environment (dev/staging/prod) has its own .env file

Author: Group 2 - Vendor Intelligence Team
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    SECURITY:
    - Database credentials have NO defaults - must be in .env
    - Non-sensitive settings (like API prefix) can have defaults
    - All values validated by Pydantic for type safety
    """
    
    # ============================================
    # API SETTINGS (Safe to have defaults)
    # ============================================
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Vendor Intelligence API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Vendor Performance Tracking and Selection System"
    
    # ============================================
    # DATABASE SETTINGS (NO DEFAULTS - Security!)
    # ============================================
    # These MUST be provided in .env file
    # NO default values to prevent accidental exposure
    
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # ============================================
    # DATABASE POOL SETTINGS (Safe defaults)
    # ============================================
    # These are not sensitive - business logic settings
    
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600  # 1 hour in seconds
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False  # Set to True to see SQL queries in logs
    
    # ============================================
    # PERFORMANCE SCORING WEIGHTS (Safe defaults)
    # ============================================
    # Business logic - not sensitive information
    # Must sum to 1.0
    
    WEIGHT_ONTIME_DELIVERY: float = 0.30
    WEIGHT_COST_COMPETITIVENESS: float = 0.25
    WEIGHT_EXCEPTION_RATE: float = 0.20
    WEIGHT_CAPACITY_UTILIZATION: float = 0.15
    WEIGHT_POD_COMPLIANCE: float = 0.10
    
    # ============================================
    # ENVIRONMENT SETTINGS (Safe defaults)
    # ============================================
    
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # ============================================
    # COMPUTED PROPERTIES
    # ============================================
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct database URL from components
        All components loaded from .env for security
        
        Returns:
            str: Complete database connection URL
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """
        Construct async database URL (for future async operations)
        
        Returns:
            str: Async database connection URL
        """
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    # ============================================
    # PYDANTIC CONFIGURATION
    # ============================================
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Provide helpful error messages
        @staticmethod
        def json_schema_extra(schema, model):
            """Add examples to schema"""
            schema['examples'] = [{
                "DB_HOST": "157.180.28.78",
                "DB_PORT": 3306,
                "DB_NAME": "group2_vendor_intel",
                "DB_USER": "your_username",
                "DB_PASSWORD": "your_password"
            }]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Using lru_cache ensures settings are loaded only once
    and reused across the application for performance
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Create global settings instance
settings = get_settings()


def validate_weights():
    """
    Validate that scoring weights sum to 1.0
    
    Raises:
        ValueError: If weights don't sum to 1.0 (within 0.001 tolerance)
    """
    total = (
        settings.WEIGHT_ONTIME_DELIVERY +
        settings.WEIGHT_COST_COMPETITIVENESS +
        settings.WEIGHT_EXCEPTION_RATE +
        settings.WEIGHT_CAPACITY_UTILIZATION +
        settings.WEIGHT_POD_COMPLIANCE
    )
    
    if abs(total - 1.0) > 0.001:
        raise ValueError(
            f"❌ Scoring weights must sum to 1.0, currently sum to {total}. "
            f"Please check your .env file.\n"
            f"Current weights:\n"
            f"  WEIGHT_ONTIME_DELIVERY: {settings.WEIGHT_ONTIME_DELIVERY}\n"
            f"  WEIGHT_COST_COMPETITIVENESS: {settings.WEIGHT_COST_COMPETITIVENESS}\n"
            f"  WEIGHT_EXCEPTION_RATE: {settings.WEIGHT_EXCEPTION_RATE}\n"
            f"  WEIGHT_CAPACITY_UTILIZATION: {settings.WEIGHT_CAPACITY_UTILIZATION}\n"
            f"  WEIGHT_POD_COMPLIANCE: {settings.WEIGHT_POD_COMPLIANCE}"
        )


def validate_database_config():
    """
    Validate that all required database settings are present
    
    Raises:
        ValueError: If any required database setting is missing
    """
    required_fields = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_fields = []
    
    for field in required_fields:
        try:
            value = getattr(settings, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        except AttributeError:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(
            f"❌ Missing required database configuration:\n"
            f"  {', '.join(missing_fields)}\n\n"
            f"Please ensure these are set in your .env file.\n"
            f"See .env.example for template."
        )


# Validate configuration on module import
try:
    validate_weights()
    validate_database_config()
except Exception as e:
    import sys
    print(f"\n{'=' * 60}")
    print(f"⚠️  CONFIGURATION ERROR")
    print(f"{'=' * 60}")
    print(f"{str(e)}")
    print(f"{'=' * 60}\n")
    # Don't exit - let the application handle it