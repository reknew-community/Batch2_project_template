"""
Base Classes for SQLAlchemy Models

Provides:
    - Base: Declarative base for all models
    - TimestampMixin: Adds created_at and updated_at fields
    - BaseModel: Base model with id, timestamps, and utility methods

Author: Group 2 - Vendor Intelligence Team
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from typing import Any, Dict

# Create declarative base
Base = declarative_base()


class TimestampMixin:
    """
    Mixin class to add automatic timestamp tracking to models
    
    Adds:
        - created_at: Timestamp when record was created
        - updated_at: Timestamp when record was last updated (auto-updates)
    
    Usage:
        class MyModel(BaseModel, TimestampMixin):
            pass
    """
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when record was last updated"
    )


class BaseModel(Base, TimestampMixin):
    """
    Base model class for all database models
    
    Provides:
        - id: Primary key (auto-increment)
        - created_at: Creation timestamp (from TimestampMixin)
        - updated_at: Update timestamp (from TimestampMixin)
        - to_dict(): Convert model to dictionary
        - __repr__(): String representation
    
    Usage:
        class Vendor(BaseModel):
            __tablename__ = "vendors"
            name = Column(String(255))
    """
    
    __abstract__ = True  # Tell SQLAlchemy not to create table for this class
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="Primary key - auto-incrementing integer"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Useful for:
            - API responses
            - JSON serialization
            - Debugging
        
        Returns:
            dict: Dictionary with all column names and values
            
        Example:
            vendor = db.query(Vendor).first()
            vendor_dict = vendor.to_dict()
            # {"id": 1, "name": "ABC Logistics", ...}
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """
        String representation of model instance
        
        Returns:
            str: Human-readable representation
            
        Example:
            print(vendor)
            # <Vendor(id=1)>
        """
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"