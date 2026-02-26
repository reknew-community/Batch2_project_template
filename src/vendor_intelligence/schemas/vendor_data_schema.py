from pydantic import BaseModel, EmailStr
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any


class VendorBase(BaseModel):
    id: int
    vendor_code: str
    name: str

    vendor_type: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None

    pricing_model: Optional[str] = None
    base_rate: Optional[Decimal] = None

    total_capacity: Optional[int] = None
    available_capacity: Optional[int] = None

    service_areas: Optional[Any] = None  # JSON field

    is_active: bool

    created_ts: datetime
    updated_ts: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class VendorResponse(VendorBase):
    """Response model for GET vendor endpoints"""
    pass