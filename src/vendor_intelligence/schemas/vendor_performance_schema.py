from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Literal


class VendorPerformanceBase(BaseModel):
    vendor_id: int
    calculated_date: date
    period_type: Literal["Monthly", "Weekly", "Daily"]

    # ---- Trip Metrics ----
    total_trips: int
    completed_trips: int
    cancelled_trips: int

    # ---- On-Time Metrics ----
    ontime_pickups: int
    ontime_pickup_rate: Decimal

    ontime_deliveries: int
    ontime_delivery_rate: Decimal

    # ---- Exceptions ----
    total_exceptions: int
    exception_rate: Decimal

    # ---- Cost & Utilization ----
    avg_cost_per_kg: Decimal
    avg_cost_per_trip: Decimal
    avg_capacity_utilization_pct: Decimal

    # ---- Final Score ----
    performance_score: Decimal

    # ---- Audit Fields ----
    created_ts: date
    updated_ts: date

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class VendorPerformanceResponse(VendorPerformanceBase):
    """Response model for GET vendor performance endpoint"""
    pass