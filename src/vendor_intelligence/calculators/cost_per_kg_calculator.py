from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP


async def calculate_cost_competitiveness(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:

    try:
        query = text("""
            SELECT 
                COALESCE(SUM(actual_cost), 0) AS aggr_total_cost,
                COALESCE(SUM(weight_kg), 0) AS aggr_weight_kg
            FROM shipments
            WHERE assigned_vendor_id = :vendor_id
              AND booking_date >= :start_date
              AND booking_date <= :end_date
        """)

        query_market_rate = text("""
            SELECT 
                COALESCE(SUM(actual_cost), 0) AS aggr_total_cost,
                COALESCE(SUM(weight_kg), 0) AS aggr_weight_kg
            FROM shipments
            WHERE booking_date >= :start_date
              AND booking_date <= :end_date
        """)

        row = db.execute(
            query,
            {
                "vendor_id": vendor_id,
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()

        row_market = db.execute(
            query_market_rate,
            {
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()

        if row is None or row_market is None:
            raise ValueError("Database returned no aggregation results")

        total_cost_vendor = Decimal(row.aggr_total_cost or 0)
        weight_kg_vendor = Decimal(row.aggr_weight_kg or 0)
        total_cost_market = Decimal(row_market.aggr_total_cost or 0)
        weight_kg_market = Decimal(row_market.aggr_weight_kg or 0)

        # Vendor has no shipments
        if weight_kg_vendor == 0:
            return {
                "vendor_id": vendor_id,
                "metric": "cost_per_kg",
                "score": 0.0,
                "raw_data": None,
                "warning": "Vendor has no shipment weight in selected period",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        # Market has no shipments
        if weight_kg_market == 0:
            return {
                "vendor_id": vendor_id,
                "metric": "cost_per_kg",
                "score": 50.0,
                "raw_data": None,
                "warning": "Market shipment weight is zero; default neutral score applied",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        cost_per_kg = (
            total_cost_vendor / weight_kg_vendor
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        market_rate_per_kg = (
            total_cost_market / weight_kg_market
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # Extra protection
        if market_rate_per_kg == Decimal("0"):
            score = Decimal("50")
        else:
            cost_ratio = cost_per_kg / market_rate_per_kg

            if cost_ratio <= Decimal("0.8"):
                score = Decimal("100")
            elif cost_ratio <= Decimal("1.0"):
                score = Decimal("75") + (Decimal("1.0") - cost_ratio) * Decimal("125")
            elif cost_ratio <= Decimal("1.5"):
                score = Decimal("75") - (cost_ratio - Decimal("1.0")) * Decimal("120")
            else:
                score = Decimal("0")
        
        score = max(Decimal("0"), min(Decimal("100"), score))
        score = score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "vendor_id": vendor_id,
            "metric": "cost_per_kg",
            "score": float(score),
            "raw_data": {
                "vendor": {
                    "total_cost": float(total_cost_vendor),
                    "weight_kg": float(weight_kg_vendor),
                    "cost_per_kg": float(cost_per_kg)
                },
                "market": {
                    "total_cost": float(total_cost_market),
                    "weight_kg": float(weight_kg_market),
                    "market_rate_per_kg": float(market_rate_per_kg)
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except ZeroDivisionError:
        return {
            "vendor_id": vendor_id,
            "metric": "cost_per_kg",
            "score": 0.0,
            "raw_data": None,
            "error": "Division by zero encountered during cost calculation",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except ValueError as ve:
        return {
            "vendor_id": vendor_id,
            "metric": "cost_per_kg",
            "score": 0.0,
            "raw_data": None,
            "error": str(ve),
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except Exception as e:
        return {
            "vendor_id": vendor_id,
            "metric": "cost_per_kg",
            "score": 0.0,
            "raw_data": None,
            "error": f"Unexpected error: {str(e)}",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
