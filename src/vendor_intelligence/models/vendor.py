"""
Vendor Model

Represents logistics vendor master data

Author: Group 2 - Vendor Intelligence Team
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from vendor_intelligence.database.base import BaseModel


class VendorType(str, enum.Enum):
    """
    Vendor type enumeration
    
    Types:
        FTL: Full Truck Load
        PART_LOAD: Partial truck load
        LAST_MILE: Last mile delivery service
        THREE_PL: Third-party logistics provider
    """
    FTL = "FTL"
    PART_LOAD = "PART_LOAD"
    LAST_MILE = "LAST_MILE"
    THREE_PL = "3PL"


class PricingModel(str, enum.Enum):
    """
    Pricing model enumeration
    
    Models:
        PER_TRIP: Charged per trip
        PER_KG: Charged per kilogram
        PER_BOX: Charged per box/package
        FIXED_RATE: Fixed monthly/contract rate
    """
    PER_TRIP = "PER_TRIP"
    PER_KG = "PER_KG"
    PER_BOX = "PER_BOX"
    FIXED_RATE = "FIXED_RATE"


class Vendor(BaseModel):
    """
    Vendor master data model
    
    Stores information about logistics vendors including:
        - Basic information (name, code)
        - Contact details
        - Vendor type and pricing
        - Capacity
        - Active status
    
    Relationships:
        - trips: One-to-Many relationship with Trip model
    """
    
    __tablename__ = "vendors"
    
    # ============================================
    # BASIC INFORMATION
    # ============================================
    
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Vendor company name"
    )
    
    vendor_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique vendor identifier code"
    )
    
    # ============================================
    # CONTACT INFORMATION
    # ============================================
    
    contact_person = Column(
        String(255),
        comment="Primary contact person name"
    )
    
    email = Column(
        String(255),
        comment="Contact email address"
    )
    
    phone = Column(
        String(50),
        comment="Contact phone number"
    )
    
    address = Column(
        String(500),
        comment="Full street address"
    )
    
    city = Column(
        String(100),
        comment="City"
    )
    
    state = Column(
        String(50),
        comment="State/Province"
    )
    
    pincode = Column(
        String(20),
        comment="Postal/ZIP code"
    )
    
    # ============================================
    # VENDOR DETAILS
    # ============================================
    
    vendor_type = Column(
        SQLEnum(VendorType),
        nullable=False,
        comment="Type of logistics vendor"
    )
    
    pricing_model = Column(
        SQLEnum(PricingModel),
        nullable=False,
        comment="Pricing model used by vendor"
    )
    
    base_rate = Column(
        Float,
        nullable=False,
        comment="Base rate in rupees (interpretation depends on pricing_model)"
    )
    
    # ============================================
    # CAPACITY
    # ============================================
    
    capacity = Column(
        Integer,
        comment="Total capacity in kg or units"
    )
    
    # ============================================
    # STATUS
    # ============================================
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether vendor is currently active"
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether vendor has been verified"
    )
    
    # ============================================
    # RELATIONSHIPS
    # ============================================
    
    trips = relationship(
        "Trip",
        back_populates="vendor",
        lazy="dynamic"
    )
    
    def __repr__(self):
        """String representation"""
        return (
            f"<Vendor("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"code='{self.vendor_code}', "
            f"type='{self.vendor_type.value}'"
            f")>"
        )