"""
Trip Model

Represents individual shipment/trip data

Author: Group 2 - Vendor Intelligence Team
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from vendor_intelligence.database.base import BaseModel


class Trip(BaseModel):
    """
    Trip/Shipment data model
    
    Stores information about individual shipments including:
        - Trip identification (AWB number)
        - Route information via hub references
        - Shipment details (weight, cost)
        - Scheduled vs actual times
        - Status and exceptions
        - POD (Proof of Delivery) information
    
    Relationships:
        - vendor: Many-to-One relationship with Vendor model
    """
    
    __tablename__ = "trips_test"
    
    # ============================================
    # TRIP IDENTIFICATION
    # ============================================
    
    awb_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Air Waybill number - unique shipment identifier"
    )
    
    # ============================================
    # FOREIGN KEYS
    # ============================================
    
    customer_id = Column(
        Integer,
        index=True,
        comment="Reference to customer"
    )
    
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id"),
        nullable=False,
        index=True,
        comment="Reference to vendor handling this shipment"
    )
    
    origin_hub_id = Column(
        Integer,
        comment="Reference to origin hub"
    )
    
    destination_hub_id = Column(
        Integer,
        comment="Reference to destination hub"
    )
    
    # ============================================
    # ROUTE INFORMATION
    # ============================================
    
    route_code = Column(
        String(100),
        index=True,
        comment="Route identifier code"
    )
    
    # ============================================
    # SCHEDULED TIMES
    # ============================================
    
    scheduled_pickup_time = Column(
        DateTime,
        nullable=False,
        comment="Scheduled time for pickup"
    )
    
    scheduled_delivery_time = Column(
        DateTime,
        nullable=False,
        comment="Scheduled time for delivery"
    )
    
    # ============================================
    # ACTUAL TIMES
    # ============================================
    
    actual_pickup_time = Column(
        DateTime,
        comment="Actual time when pickup occurred"
    )
    
    actual_delivery_time = Column(
        DateTime,
        comment="Actual time when delivery occurred"
    )
    
    # ============================================
    # SHIPMENT DETAILS
    # ============================================
    
    weight_kg = Column(
        Float,
        nullable=False,
        comment="Total weight in kilograms"
    )
    
    total_cost = Column(
        Float,
        nullable=False,
        comment="Total freight cost in rupees"
    )
    
    cost_per_kg = Column(
        Float,
        comment="Pre-calculated cost per kilogram"
    )
    
    # ============================================
    # STATUS
    # ============================================
    
    status = Column(
        String(50),
        index=True,
        comment="Current trip status (PENDING, IN_TRANSIT, DELIVERED, CANCELLED)"
    )
    
    # ============================================
    # DATES
    # ============================================
    
    booking_date = Column(
        Date,
        comment="Date when shipment was booked"
    )
    
    delivery_date = Column(
        Date,
        comment="Date when shipment was delivered"
    )
    
    # ============================================
    # EXCEPTION INFORMATION
    # ============================================
    
    has_exception = Column(
        Boolean,
        default=False,
        comment="Whether trip has any exceptions"
    )
    
    exception_type = Column(
        String(100),
        comment="Type of exception (DELAY, DAMAGE, SHORT, LOST)"
    )
    
    exception_description = Column(
        Text,
        comment="Detailed description of the exception"
    )
    
    exception_reported_at = Column(
        DateTime,
        comment="When the exception was reported"
    )
    
    # ============================================
    # POD INFORMATION
    # ============================================
    
    pod_uploaded = Column(
        Boolean,
        default=False,
        comment="Whether POD document has been uploaded"
    )
    
    pod_upload_timestamp = Column(
        DateTime,
        comment="When POD document was uploaded"
    )
    
    pod_url = Column(
        String(500),
        comment="URL to POD document"
    )
    
    # ============================================
    # SHIPMENT CLASSIFICATION
    # ============================================
    
    priority = Column(
        String(50),
        comment="Shipment priority level (HIGH, MEDIUM, LOW)"
    )
    
    shipment_type = Column(
        String(50),
        comment="Type of shipment (EXPRESS, STANDARD, ECONOMY)"
    )
    
    special_instructions = Column(
        Text,
        comment="Special handling instructions"
    )
    
    # ============================================
    # RELATIONSHIPS
    # ============================================
    
    vendor = relationship(
        "Vendor",
        back_populates="trips"
    )
    
    # ============================================
    # COMPUTED PROPERTIES
    # ============================================
    
    @property
    def calculated_cost_per_kg(self) -> float:
        """
        Calculate cost per kilogram for this trip
        
        Returns:
            float: Cost per kg, or stored value if available, or 0.0 if weight is zero
        """
        # Use pre-calculated value if available
        if self.cost_per_kg is not None:
            return self.cost_per_kg
            
        # Otherwise calculate on the fly
        if self.weight_kg and self.weight_kg > 0:
            return round(self.total_cost / self.weight_kg, 2)
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """
        Check if trip is completed
        
        Returns:
            bool: True if status is DELIVERED and actual delivery time is set
        """
        return (
            self.status == "DELIVERED" and
            self.actual_delivery_time is not None
        )
    
    @property
    def is_pickup_ontime(self) -> bool:
        """
        Check if pickup was on time
        
        Returns:
            bool: True if actual pickup <= scheduled pickup, False otherwise
        """
        if self.scheduled_pickup_time and self.actual_pickup_time:
            return self.actual_pickup_time <= self.scheduled_pickup_time
        return False
    
    @property
    def is_delivery_ontime(self) -> bool:
        """
        Check if delivery was on time
        
        Returns:
            bool: True if actual delivery <= scheduled delivery, False otherwise
        """
        if self.scheduled_delivery_time and self.actual_delivery_time:
            return self.actual_delivery_time <= self.scheduled_delivery_time
        return False
    
    @property
    def pickup_delay_hours(self) -> float:
        """
        Calculate pickup delay in hours
        
        Returns:
            float: Hours delayed (positive if late, negative if early, 0 if no delay)
        """
        if self.scheduled_pickup_time and self.actual_pickup_time:
            delta = self.actual_pickup_time - self.scheduled_pickup_time
            return round(delta.total_seconds() / 3600, 2)
        return 0.0
    
    @property
    def delivery_delay_hours(self) -> float:
        """
        Calculate delivery delay in hours
        
        Returns:
            float: Hours delayed (positive if late, negative if early, 0 if no delay)
        """
        if self.scheduled_delivery_time and self.actual_delivery_time:
            delta = self.actual_delivery_time - self.scheduled_delivery_time
            return round(delta.total_seconds() / 3600, 2)
        return 0.0
    
    def __repr__(self):
        """String representation"""
        return (
            f"<Trip("
            f"id={self.id}, "
            f"awb='{self.awb_number}', "
            f"vendor_id={self.vendor_id}, "
            f"status='{self.status}'"
            f")>"
        )